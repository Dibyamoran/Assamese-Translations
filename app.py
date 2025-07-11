import os
import logging
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)

# Create tables - Need to put this here to make it work with Gunicorn
with app.app_context():
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")

# Import auth components
from replit_auth import make_replit_blueprint

# Register the auth blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Translation APIs configuration
MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"
LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"

@app.route('/')
def index():
    """Main page with translation interface"""
    return render_template('index.html')

@app.route('/history')
def history():
    """Translation history page for logged in users"""
    if not current_user.is_authenticated:
        return redirect(url_for('replit_auth.login'))
    
    from models import Translation
    translations = Translation.query.filter_by(user_id=current_user.id).order_by(Translation.created_at.desc()).limit(50).all()
    
    return render_template('history.html', translations=translations)

def translate_with_mymemory(text):
    """Translate using MyMemory API (free, no API key required)"""
    try:
        params = {
            'q': text,
            'langpair': 'en|as'  # English to Assamese
        }
        
        response = requests.get(
            MYMEMORY_API_URL,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('responseStatus') == 200:
                translated_text = result.get('responseData', {}).get('translatedText', '')
                return translated_text.strip() if translated_text else None
        
        return None
    except Exception as e:
        app.logger.error(f"MyMemory API error: {str(e)}")
        return None

def translate_with_libretranslate(text):
    """Translate using LibreTranslate API (requires API key)"""
    try:
        api_key = os.environ.get("LIBRETRANSLATE_API_KEY")
        translation_data = {
            'q': text,
            'source': 'en',
            'target': 'as',
            'format': 'text'
        }
        
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        response = requests.post(
            LIBRETRANSLATE_API_URL,
            json=translation_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result.get('translatedText', '')
            return translated_text.strip() if translated_text else None
        
        return None
    except Exception as e:
        app.logger.error(f"LibreTranslate API error: {str(e)}")
        return None

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text from English to Assamese using multiple translation services"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Please enter some text to translate'
            }), 400
        
        # Try MyMemory first (free, no API key needed)
        app.logger.info("Attempting translation with MyMemory API")
        translated_text = translate_with_mymemory(text)
        
        if translated_text:
            # Save translation history if user is logged in
            if current_user.is_authenticated:
                try:
                    from models import Translation
                    translation = Translation(
                        user_id=current_user.id,
                        original_text=text,
                        translated_text=translated_text,
                        service_used='MyMemory'
                    )
                    db.session.add(translation)
                    db.session.commit()
                except Exception as e:
                    app.logger.error(f"Failed to save translation history: {str(e)}")
                    
            return jsonify({
                'success': True,
                'translated_text': translated_text,
                'original_text': text,
                'service': 'MyMemory'
            })
        
        # If MyMemory fails, try LibreTranslate (if API key is available)
        app.logger.info("MyMemory failed, attempting LibreTranslate API")
        translated_text = translate_with_libretranslate(text)
        
        if translated_text:
            # Save translation history if user is logged in
            if current_user.is_authenticated:
                try:
                    from models import Translation
                    translation = Translation(
                        user_id=current_user.id,
                        original_text=text,
                        translated_text=translated_text,
                        service_used='LibreTranslate'
                    )
                    db.session.add(translation)
                    db.session.commit()
                except Exception as e:
                    app.logger.error(f"Failed to save translation history: {str(e)}")
                    
            return jsonify({
                'success': True,
                'translated_text': translated_text,
                'original_text': text,
                'service': 'LibreTranslate'
            })
        
        # If all services fail
        return jsonify({
            'success': False,
            'error': 'Translation services are currently unavailable. Please try again later.'
        }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Translation request timed out. Please try again.'
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Unable to connect to translation service. Please check your internet connection.'
        }), 503
    except Exception as e:
        app.logger.error(f"Translation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

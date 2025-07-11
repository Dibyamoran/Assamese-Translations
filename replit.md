# English to Assamese Translator

## Overview

This is a Flask-based web application that provides real-time translation from English to Assamese. The application uses the LibreTranslate API as the translation engine and features a responsive dark-themed interface built with Bootstrap.

## System Architecture

The application follows a client-server architecture with user authentication:

- **Frontend**: Single-page application using HTML, CSS, and JavaScript
- **Backend**: Flask web server with REST API endpoints
- **Database**: PostgreSQL database for user data and translation history
- **Authentication**: Replit Auth integration with OAuth2 flow
- **Translation Service**: Multiple APIs (MyMemory primary, LibreTranslate backup)
- **Deployment**: Configured for Replit deployment with main.py entry point

## Key Components

### Backend (Flask)
- **app.py**: Main Flask application with translation endpoints and authentication
- **main.py**: Application entry point for deployment
- **models.py**: Database models for users, OAuth tokens, and translation history
- **replit_auth.py**: Authentication blueprint with OAuth2 flow
- **Translation API**: `/translate` POST endpoint with multiple service fallbacks
- **History API**: `/history` GET endpoint for user translation history

### Frontend
- **templates/index.html**: Main UI template with Bootstrap dark theme
- **static/css/style.css**: Custom styling for animations and responsive design
- **static/js/app.js**: Client-side JavaScript for form handling and API communication

### External Integration
- **LibreTranslate API**: Free translation service for English to Assamese translation
- **Bootstrap CDN**: UI framework with dark theme
- **Font Awesome**: Icon library for enhanced UI

## Data Flow

1. User enters English text in the web interface
2. JavaScript captures form submission and sends POST request to `/translate`
3. Flask server receives request and forwards to LibreTranslate API
4. Translation response is processed and returned to client
5. JavaScript updates UI with translated Assamese text

## External Dependencies

### Python Packages
- **Flask**: Web framework for backend API
- **Flask-CORS**: Cross-origin resource sharing support
- **requests**: HTTP client for API calls

### Frontend Dependencies (CDN)
- **Bootstrap**: UI framework with dark theme
- **Font Awesome**: Icon library

### External Services
- **LibreTranslate API**: Translation service (https://libretranslate.com/translate)

## Deployment Strategy

- **Platform**: Replit deployment
- **Entry Point**: main.py imports and runs the Flask app
- **Environment**: Uses environment variables for configuration
- **CORS**: Enabled for cross-origin requests

## Changelog
- July 08, 2025. Added Replit Auth integration with PostgreSQL database
  - User authentication and session management
  - Translation history tracking for logged-in users
  - User profile display and logout functionality
  - Database models for users, OAuth tokens, and translations
- July 04, 2025. Initial setup
  - Basic translation functionality with MyMemory API
  - Clean responsive UI with Bootstrap dark theme
  - Multiple translation service fallbacks

## User Preferences

Preferred communication style: Simple, everyday language.
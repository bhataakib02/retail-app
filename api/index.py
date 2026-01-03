# Vercel serverless function handler for Flask app
import sys
import os

# Add parent directory to path so we can import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from app import app
    # Export the Flask app for Vercel (WSGI application)
    handler = app
except Exception as e:
    # If import fails, create a minimal error handler
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        return f'Error loading application: {str(e)}', 500
    
    handler = error_app


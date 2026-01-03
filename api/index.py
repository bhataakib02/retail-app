"""
Vercel serverless function handler for Flask app
This is the entry point for Vercel serverless functions
"""
import sys
import os

# Add the parent directory to Python path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Flask application
# This must be done after path modification
from app import app

# Vercel expects the handler to be the WSGI application
# Export it as 'handler' which is what Vercel looks for
handler = app

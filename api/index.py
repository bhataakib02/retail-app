"""
Vercel serverless function handler for Flask app
This file exports the Flask application as a WSGI handler for Vercel
"""
import sys
import os

# Add parent directory to path so we can import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Flask app - this will initialize the application
from app import app

# Export the Flask app as the handler for Vercel
# Vercel's Python runtime expects a WSGI application
handler = app


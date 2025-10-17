"""
CORS Middleware
===============

Handles Cross-Origin Resource Sharing (CORS) for frontend-backend communication
"""

from flask_cors import CORS

def init_cors(app):
    """
    Initialize CORS middleware for the Flask app
    
    Allows frontend (running on different port) to communicate with backend API
    """
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",      # React default
                "http://localhost:5173",      # Vite default
                "http://localhost:8000",      # Python HTTP server
                "http://localhost:8080",      # Vue default
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:8080",
                "file://*",                   # Local HTML files
                "*"                           # Allow all (development only)
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "X-Total-Count"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    return app

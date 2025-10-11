"""
Supplier Clustering System - REST API
======================================

Main Flask application that serves the REST API for the frontend.
"""

from flask import Flask
from flask_cors import CORS
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
from database import db_connection

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Import and register route blueprints
from routes.companies import companies_bp
from routes.transactions import transactions_bp
from routes.recommendations import recommendations_bp

app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')
app.register_blueprint(recommendations_bp, url_prefix='/api')


@app.route('/')
def home():
    """Root endpoint - API information"""
    return {
        "message": "Supplier Clustering System API",
        "version": "1.0.0",
        "endpoints": {
            "companies": "/api/companies",
            "transactions": "/api/transactions",
            "recommendations": "/api/recommendations"
        }
    }


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = db_connection.get_database()
        collections = db.list_collection_names()
        
        return {
            "status": "healthy",
            "database": "connected",
            "collections": len(collections)
        }, 200
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500


if __name__ == '__main__':
    # Test database connection
    if db_connection.test_connection():
        print("\nDatabase connection successful!")
        print("\nStarting Flask API server...")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    else:
        print("\nCannot start API - Database connection failed")
        print("Please ensure MongoDB is running")

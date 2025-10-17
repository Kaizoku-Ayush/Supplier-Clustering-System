"""
Supplier Clustering System - REST API
======================================

Main Flask application that serves the REST API for the frontend.
"""

from flask import Flask
import sys
import os

# Add models and middleware paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'middleware'))

from database import db_connection
from middleware import init_all_middleware

# Initialize Flask app
app = Flask(__name__)

# Initialize all middleware (CORS, logging, error handlers)
app = init_all_middleware(app)

# Import and register route blueprints
from routes.auth import auth_bp
from routes.companies import companies_bp
from routes.transactions import transactions_bp
from routes.recommendations import recommendations_bp
from routes.upload import upload_bp

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')
app.register_blueprint(recommendations_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')


@app.route('/')
def home():
    """Root endpoint - API information"""
    return {
        "message": "SupplierIQ API",
        "version": "2.0.0",
        "clustering_method": "Ensemble (Voting-Based)",
        "endpoints": {
            "companies": "/api/companies",
            "transactions": "/api/transactions",
            "recommendations": "/api/recommendations",
            "upload": "/api/upload",
            "analyze": "/api/analyze (Ensemble clustering only)",
            "template": "/api/template"
        },
        "features": {
            "ensemble_clustering": "K-Means + Hierarchical + DBSCAN voting",
            "performance_tiers": "High, Mid, Low (percentage distribution)",
            "full_details": "Optional detailed analysis on request"
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
            debug=False  # Disabled to fix Python 3.13 socket issue
        )
    else:
        print("\nCannot start API - Database connection failed")
        print("Please ensure MongoDB is running")

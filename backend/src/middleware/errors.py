"""
Error Handler Middleware
========================

Centralizes error handling for consistent API responses
"""

from flask import jsonify
import traceback

def init_error_handlers(app):
    """
    Initialize error handlers for the Flask app
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': str(error)
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(error),
            'traceback': traceback.format_exc() if app.debug else None
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all uncaught exceptions"""
        return jsonify({
            'success': False,
            'error': 'Unexpected error occurred',
            'message': str(error),
            'traceback': traceback.format_exc() if app.debug else None
        }), 500
    
    return app

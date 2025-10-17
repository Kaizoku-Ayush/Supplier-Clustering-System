"""
Logging Middleware
==================

Logs all API requests and responses for debugging and monitoring
"""

from flask import request
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('api')

def init_logging(app):
    """
    Initialize request logging middleware
    """
    
    @app.before_request
    def log_request():
        """Log incoming request details"""
        request.start_time = time.time()
        
        logger.info(f"→ {request.method} {request.path}")
        
        # Log query parameters
        if request.args:
            logger.debug(f"  Query params: {dict(request.args)}")
        
        # Log request body for POST/PUT
        if request.method in ['POST', 'PUT'] and request.is_json:
            logger.debug(f"  Body: {request.get_json()}")
    
    @app.after_request
    def log_response(response):
        """Log response details and timing"""
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Log response
        status_emoji = "✅" if response.status_code < 400 else "❌"
        logger.info(
            f"{status_emoji} {request.method} {request.path} "
            f"→ {response.status_code} ({duration*1000:.2f}ms)"
        )
        
        return response
    
    return app

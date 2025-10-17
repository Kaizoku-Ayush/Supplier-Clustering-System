"""
Middleware Package
==================

Central initialization for all middleware components
"""

from .cors import init_cors
from .errors import init_error_handlers
from .logging import init_logging
from .validation import validate_json, validate_file_upload, validate_query_params

__all__ = [
    'init_cors',
    'init_error_handlers',
    'init_logging',
    'validate_json',
    'validate_file_upload',
    'validate_query_params'
]

def init_all_middleware(app):
    """
    Initialize all middleware in correct order
    
    Order matters:
    1. CORS - Must be first to handle preflight requests
    2. Logging - Log all requests
    3. Error Handlers - Catch and format errors
    """
    app = init_cors(app)
    app = init_logging(app)
    app = init_error_handlers(app)
    
    return app

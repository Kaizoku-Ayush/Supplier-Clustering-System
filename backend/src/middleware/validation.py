"""
Request Validation Middleware
==============================

Validates incoming requests for required fields and formats
"""

from flask import request, jsonify
from functools import wraps

def validate_json(required_fields=None):
    """
    Decorator to validate JSON request body
    
    Args:
        required_fields (list): List of required field names
    
    Usage:
        @validate_json(['data', 'method'])
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON content
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json'
                }), 400
            
            # Get JSON data
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request body cannot be empty'
                }), 400
            
            # Validate required fields
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required fields: {", ".join(missing)}'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_file_upload(allowed_extensions=None, max_size_mb=None):
    """
    Decorator to validate file uploads
    
    Args:
        allowed_extensions (list): List of allowed file extensions (e.g., ['csv', 'xlsx'])
        max_size_mb (int): Maximum file size in megabytes
    
    Usage:
        @validate_file_upload(['csv'], max_size_mb=10)
        def upload_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if file is present
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file uploaded'
                }), 400
            
            file = request.files['file']
            
            # Check if filename is empty
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Validate file extension
            if allowed_extensions:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                    }), 400
            
            # Validate file size
            if max_size_mb:
                file.seek(0, 2)  # Seek to end
                size_mb = file.tell() / (1024 * 1024)
                file.seek(0)  # Reset to beginning
                
                if size_mb > max_size_mb:
                    return jsonify({
                        'success': False,
                        'error': f'File too large. Maximum size: {max_size_mb}MB'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(allowed_params=None, required_params=None):
    """
    Decorator to validate query parameters
    
    Args:
        allowed_params (list): List of allowed parameter names
        required_params (list): List of required parameter names
    
    Usage:
        @validate_query_params(allowed=['limit', 'page'], required=['page'])
        def list_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate required parameters
            if required_params:
                missing = [param for param in required_params if param not in request.args]
                if missing:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required query parameters: {", ".join(missing)}'
                    }), 400
            
            # Validate allowed parameters
            if allowed_params:
                invalid = [param for param in request.args.keys() if param not in allowed_params]
                if invalid:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid query parameters: {", ".join(invalid)}',
                        'allowed': allowed_params
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

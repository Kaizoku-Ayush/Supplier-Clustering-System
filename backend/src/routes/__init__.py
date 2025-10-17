"""
Routes Package
==============
Contains all API route blueprints.
"""

from .auth import auth_bp
from .companies import companies_bp
from .transactions import transactions_bp
from .recommendations import recommendations_bp
from .upload import upload_bp

__all__ = [
    'auth_bp',
    'companies_bp',
    'transactions_bp',
    'recommendations_bp',
    'upload_bp'
]

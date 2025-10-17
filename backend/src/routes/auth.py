"""
Authentication Routes
====================
Handles user registration, login, and logout.
"""

from flask import Blueprint, request, jsonify
import jwt  # PyJWT library
import datetime
import bcrypt
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_db

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production"


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request Body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword"
        }
    
    Returns:
        {
            "success": true,
            "message": "Registration successful",
            "user": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({
                "success": False,
                "message": "Missing required fields: name, email, password"
            }), 400
        
        name = data['name']
        email = data['email'].lower()
        password = data['password']
        
        # Get users collection
        db = get_db()
        users = db['users']
        
        # Check if user already exists
        existing_user = users.find_one({"email": email})
        if existing_user:
            return jsonify({
                "success": False,
                "message": "User with this email already exists"
            }), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user_doc = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Insert user
        result = users.insert_one(user_doc)
        
        if result.inserted_id:
            return jsonify({
                "success": True,
                "message": "Registration successful",
                "user": {
                    "name": name,
                    "email": email
                }
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": "Failed to create user"
            }), 500
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({
            "success": False,
            "message": f"Registration failed: {str(e)}"
        }), 500


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Login user and return JWT token.
    
    Request Body:
        {
            "email": "john@example.com",
            "password": "securepassword"
        }
    
    Returns:
        {
            "success": true,
            "message": "Login successful",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({
                "success": False,
                "message": "Missing required fields: email, password"
            }), 400
        
        email = data['email'].lower()
        password = data['password']
        
        # Get users collection
        db = get_db()
        users = db['users']
        
        # Find user
        user = users.find_one({"email": email})
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Verify password
        # Handle both string and bytes stored passwords
        stored_password = user['password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "name": user['name'],
                "email": user['email']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            "success": False,
            "message": f"Login failed: {str(e)}"
        }), 500


@auth_bp.route('/auth/verify', methods=['GET'])
def verify_token():
    """
    Verify JWT token validity.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "success": true,
            "message": "Token is valid",
            "user": {
                "email": "john@example.com"
            }
        }
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "success": False,
                "message": "No token provided"
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return jsonify({
                "success": True,
                "message": "Token is valid",
                "user": {
                    "email": payload['email']
                }
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token has expired"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token"
            }), 401
            
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({
            "success": False,
            "message": f"Verification failed: {str(e)}"
        }), 500


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Logout user (client-side token removal).
    
    Returns:
        {
            "success": true,
            "message": "Logout successful"
        }
    """
    # Since JWT is stateless, logout is handled client-side by removing the token
    # This endpoint exists for consistency and future features (e.g., token blacklist)
    return jsonify({
        "success": True,
        "message": "Logout successful"
    }), 200

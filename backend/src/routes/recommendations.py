"""
Recommendations API Routes
==========================

Endpoints for cluster recommendations (3 ensemble clusters)
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_recommendations

# Create blueprint
recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations', methods=['GET'])
def get_all_recommendations():
    """
    Get all recommendations for ensemble clusters
    
    Query Parameters:
    - cluster_id: Filter by cluster (e.g., 0, 1, 2)
    
    Example: /api/recommendations?cluster_id=0
    """
    try:
        collection = get_recommendations()
        
        # Build query filter
        query = {}
        
        # Filter by cluster_id
        cluster_id = request.args.get('cluster_id')
        if cluster_id:
            query['cluster_id'] = int(cluster_id)
        
        # Query database
        recommendations = list(collection.find(query, {'_id': 0}))
        
        return jsonify({
            'success': True,
            'count': len(recommendations),
            'data': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendations_bp.route('/recommendations/<int:cluster_id>', methods=['GET'])
def get_recommendation_by_cluster(cluster_id):
    """
    Get recommendation for a specific cluster
    
    Example: /api/recommendations/0
    """
    try:
        collection = get_recommendations()
        
        recommendation = collection.find_one({'cluster_id': cluster_id}, {'_id': 0})
        
        if recommendation:
            return jsonify({
                'success': True,
                'data': recommendation
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Recommendation for cluster {cluster_id} not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

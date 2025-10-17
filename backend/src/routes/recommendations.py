"""
Recommendations Routes
======================
Handles cluster-level strategic recommendations.
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_recommendations

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations', methods=['GET'])
def get_all_recommendations():
    """
    Get all cluster recommendations.
    
    Query Parameters:
        - cluster (optional): Filter by cluster_id
    
    Returns:
        {
            "success": true,
            "count": 3,
            "recommendations": [
                {
                    "cluster_id": 0,
                    "profile": "Premium Suppliers",
                    "size": 130,
                    "percentage": 4.3,
                    "key_strengths": ["Quality Score", "Delivery Reliability"],
                    "improvement_areas": ["Cost Efficiency"],
                    "recommended_strategy": "Maintain partnership..."
                },
                ...
            ]
        }
    """
    try:
        recommendations = get_recommendations()
        
        # Build query filter
        query = {}
        
        # Filter by cluster
        cluster_param = request.args.get('cluster')
        if cluster_param:
            query['cluster_id'] = int(cluster_param)
        
        # Execute query
        results = list(recommendations.find(query).sort('cluster_id', 1))
        
        # Convert ObjectId to string
        for rec in results:
            rec['_id'] = str(rec['_id'])
        
        return jsonify({
            "success": True,
            "count": len(results),
            "recommendations": results
        }), 200
        
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch recommendations: {str(e)}"
        }), 500


@recommendations_bp.route('/recommendations/<int:cluster_id>', methods=['GET'])
def get_recommendation_by_cluster(cluster_id):
    """
    Get recommendation for a specific cluster.
    
    Returns:
        {
            "success": true,
            "recommendation": {...}
        }
    """
    try:
        recommendations = get_recommendations()
        
        recommendation = recommendations.find_one({"cluster_id": cluster_id})
        
        if not recommendation:
            return jsonify({
                "success": False,
                "message": f"Recommendation for cluster {cluster_id} not found"
            }), 404
        
        # Convert ObjectId to string
        recommendation['_id'] = str(recommendation['_id'])
        
        return jsonify({
            "success": True,
            "recommendation": recommendation
        }), 200
        
    except Exception as e:
        print(f"Error fetching recommendation: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch recommendation: {str(e)}"
        }), 500

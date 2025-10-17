"""
Companies Routes
================
Handles company-level data and statistics.
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_companies

companies_bp = Blueprint('companies', __name__)


@companies_bp.route('/companies', methods=['GET'])
def get_all_companies():
    """
    Get all companies with their clustering results.
    
    Query Parameters:
        - cluster (optional): Filter by cluster_id
        - tier (optional): Filter by performance_tier
        - search (optional): Search by supplier_id or company_name
    
    Returns:
        {
            "success": true,
            "count": 25,
            "companies": [...]
        }
    """
    try:
        companies = get_companies()
        
        # Build query filter
        query = {}
        
        # Filter by cluster
        cluster_param = request.args.get('cluster')
        if cluster_param:
            query['cluster_id'] = int(cluster_param)
        
        # Filter by tier
        tier_param = request.args.get('tier')
        if tier_param:
            query['performance_tier'] = tier_param
        
        # Search by supplier_id or company_name
        search_param = request.args.get('search')
        if search_param:
            query['$or'] = [
                {'supplier_id': {'$regex': search_param, '$options': 'i'}},
                {'company_name': {'$regex': search_param, '$options': 'i'}}
            ]
        
        # Execute query
        results = list(companies.find(query))
        
        # Convert ObjectId to string
        for company in results:
            company['_id'] = str(company['_id'])
        
        return jsonify({
            "success": True,
            "count": len(results),
            "companies": results
        }), 200
        
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch companies: {str(e)}"
        }), 500


@companies_bp.route('/companies/<supplier_id>', methods=['GET'])
def get_company_by_id(supplier_id):
    """
    Get a single company by supplier_id.
    
    Returns:
        {
            "success": true,
            "company": {...}
        }
    """
    try:
        companies = get_companies()
        
        company = companies.find_one({"supplier_id": supplier_id})
        
        if not company:
            return jsonify({
                "success": False,
                "message": f"Company with supplier_id '{supplier_id}' not found"
            }), 404
        
        # Convert ObjectId to string
        company['_id'] = str(company['_id'])
        
        return jsonify({
            "success": True,
            "company": company
        }), 200
        
    except Exception as e:
        print(f"Error fetching company: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch company: {str(e)}"
        }), 500


@companies_bp.route('/companies/stats', methods=['GET'])
def get_companies_stats():
    """
    Get statistics about companies.
    
    Returns:
        {
            "success": true,
            "stats": {
                "total": 25,
                "by_tier": {
                    "High Performance": 8,
                    "Mid Performance": 10,
                    "Low Performance": 7
                },
                "by_cluster": {
                    "0": 8,
                    "1": 10,
                    "2": 7
                },
                "average_scores": {
                    "overall_score": 75.5,
                    "quality_score": 78.2,
                    ...
                }
            }
        }
    """
    try:
        companies = get_companies()
        
        # Total count
        total = companies.count_documents({})
        
        # Count by tier
        pipeline_tier = [
            {"$group": {
                "_id": "$performance_tier",
                "count": {"$sum": 1}
            }}
        ]
        tier_results = list(companies.aggregate(pipeline_tier))
        by_tier = {item['_id']: item['count'] for item in tier_results}
        
        # Count by cluster
        pipeline_cluster = [
            {"$group": {
                "_id": "$cluster_id",
                "count": {"$sum": 1}
            }}
        ]
        cluster_results = list(companies.aggregate(pipeline_cluster))
        by_cluster = {str(item['_id']): item['count'] for item in cluster_results}
        
        # Average scores
        pipeline_avg = [
            {"$group": {
                "_id": None,
                "overall_score": {"$avg": "$performance.overall_score"},
                "quality_score": {"$avg": "$performance.quality_score"},
                "delivery_reliability": {"$avg": "$performance.delivery_reliability"},
                "cost_efficiency": {"$avg": "$performance.cost_efficiency"},
                "customer_satisfaction": {"$avg": "$performance.customer_satisfaction"},
                "defect_rate": {"$avg": "$performance.defect_rate"}
            }}
        ]
        avg_results = list(companies.aggregate(pipeline_avg))
        average_scores = avg_results[0] if avg_results else {}
        if average_scores:
            del average_scores['_id']
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "by_tier": by_tier,
                "by_cluster": by_cluster,
                "average_scores": average_scores
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch stats: {str(e)}"
        }), 500

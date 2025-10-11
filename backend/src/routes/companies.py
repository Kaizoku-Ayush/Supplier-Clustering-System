"""
Companies API Routes
====================

Endpoints for company-level data (25 companies with ensemble clustering)
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_companies

# Create blueprint
companies_bp = Blueprint('companies', __name__)


@companies_bp.route('/companies', methods=['GET'])
def get_all_companies():
    """
    Get all 25 companies with their ensemble clustering results
    
    Query Parameters:
    - tier: Filter by performance tier (e.g., "High Performance", "Mid Performance", "Low Performance")
    - sort_by: Sort field (default: "performance.overall_score")
    - order: Sort order "asc" or "desc" (default: "desc")
    
    Example: /api/companies?tier=High Performance&sort_by=performance.overall_score&order=desc
    """
    try:
        collection = get_companies()
        
        # Build query filter
        query = {}
        
        # Filter by performance tier
        tier = request.args.get('tier')
        if tier:
            query['performance_tier'] = tier
        
        # Filter by cluster_id
        cluster_id = request.args.get('cluster_id')
        if cluster_id:
            query['cluster_id'] = int(cluster_id)
        
        # Sorting
        sort_by = request.args.get('sort_by', 'performance.overall_score')
        order = request.args.get('order', 'desc')
        sort_direction = -1 if order == 'desc' else 1
        
        # Query database
        companies = list(collection.find(query, {'_id': 0}).sort(sort_by, sort_direction))
        
        return jsonify({
            'success': True,
            'count': len(companies),
            'data': companies
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@companies_bp.route('/companies/<supplier_id>', methods=['GET'])
def get_company_by_id(supplier_id):
    """
    Get a single company by supplier_id
    
    Example: /api/companies/SUP_001
    """
    try:
        collection = get_companies()
        
        company = collection.find_one({'supplier_id': supplier_id}, {'_id': 0})
        
        if company:
            return jsonify({
                'success': True,
                'data': company
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Company {supplier_id} not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@companies_bp.route('/companies/stats/summary', methods=['GET'])
def get_companies_summary():
    """
    Get summary statistics for all companies
    
    Returns:
    - Total companies count
    - Performance tier distribution
    - Cluster distribution
    - Average scores
    
    Example: /api/companies/stats/summary
    """
    try:
        collection = get_companies()
        
        # Get all companies
        companies = list(collection.find({}, {'_id': 0}))
        
        # Calculate tier distribution
        tier_distribution = {}
        cluster_distribution = {}
        total_score = 0
        
        for company in companies:
            # Tier distribution
            tier = company.get('performance_tier', 'Unknown')
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            # Cluster distribution
            cluster = company.get('cluster_id', -1)
            cluster_distribution[cluster] = cluster_distribution.get(cluster, 0) + 1
            
            # Total score
            total_score += company.get('performance', {}).get('overall_score', 0)
        
        avg_score = total_score / len(companies) if companies else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_companies': len(companies),
                'tier_distribution': tier_distribution,
                'cluster_distribution': cluster_distribution,
                'average_overall_score': round(avg_score, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

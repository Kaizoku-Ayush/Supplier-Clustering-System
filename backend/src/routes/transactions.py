"""
Transactions API Routes
=======================

Endpoints for transaction-level data (2,994 transactions with ensemble clustering)
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_transactions

# Create blueprint
transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    """
    Get all transactions with pagination
    
    Query Parameters:
    - supplier_id: Filter by company (e.g., "SUP_001")
    - cluster_id: Filter by cluster (e.g., 0, 1, 2)
    - performance_tier: Filter by tier (e.g., "High Performance")
    - limit: Number of results per page (default: 100, max: 500)
    - page: Page number (default: 1)
    - sort_by: Sort field (default: "transaction_date")
    - order: Sort order "asc" or "desc" (default: "desc")
    
    Example: /api/transactions?supplier_id=SUP_001&limit=50&page=1
    """
    try:
        collection = get_transactions()
        
        # Build query filter
        query = {}
        
        # Filter by supplier_id
        supplier_id = request.args.get('supplier_id')
        if supplier_id:
            query['supplier.supplier_id'] = supplier_id
        
        # Filter by cluster_id
        cluster_id = request.args.get('cluster_id')
        if cluster_id:
            query['cluster_id'] = int(cluster_id)
        
        # Filter by performance_tier
        performance_tier = request.args.get('performance_tier')
        if performance_tier:
            query['performance_tier'] = performance_tier
        
        # Pagination
        limit = min(int(request.args.get('limit', 100)), 500)  # Max 500
        page = int(request.args.get('page', 1))
        skip = (page - 1) * limit
        
        # Sorting
        sort_by = request.args.get('sort_by', 'transaction_date')
        order = request.args.get('order', 'desc')
        sort_direction = -1 if order == 'desc' else 1
        
        # Get total count for pagination
        total_count = collection.count_documents(query)
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        # Query database
        transactions = list(
            collection.find(query, {'_id': 0})
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        
        return jsonify({
            'success': True,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages
            },
            'data': transactions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@transactions_bp.route('/transactions/stats', methods=['GET'])
def get_transactions_stats():
    """
    Get statistics about transactions
    
    Query Parameters:
    - supplier_id: Filter by company (optional)
    
    Example: /api/transactions/stats?supplier_id=SUP_001
    """
    try:
        collection = get_transactions()
        
        # Build query filter
        query = {}
        supplier_id = request.args.get('supplier_id')
        if supplier_id:
            query['supplier.supplier_id'] = supplier_id
        
        # Get transactions
        transactions = list(collection.find(query, {'_id': 0}))
        
        if not transactions:
            return jsonify({
                'success': True,
                'data': {
                    'total_transactions': 0,
                    'message': 'No transactions found'
                }
            }), 200
        
        # Calculate statistics
        tier_distribution = {}
        cluster_distribution = {}
        total_score = 0
        
        for trans in transactions:
            # Tier distribution
            tier = trans.get('performance_tier', 'Unknown')
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            # Cluster distribution
            cluster = trans.get('cluster_id', -1)
            cluster_distribution[cluster] = cluster_distribution.get(cluster, 0) + 1
            
            # Total score
            total_score += trans.get('metrics', {}).get('overall_score', 0)
        
        avg_score = total_score / len(transactions)
        
        return jsonify({
            'success': True,
            'data': {
                'total_transactions': len(transactions),
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

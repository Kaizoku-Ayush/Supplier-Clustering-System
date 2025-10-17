"""
Transactions Routes
===================
Handles transaction-level data with pagination.
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add models path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from database import get_transactions

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    """
    Get all transactions with pagination.
    
    Query Parameters:
        - page (optional): Page number (default: 1)
        - limit (optional): Items per page (default: 25)
        - cluster (optional): Filter by cluster_id
        - tier (optional): Filter by performance_tier
        - supplier_id (optional): Filter by supplier_id
        - search (optional): Search by supplier_id or company_name
    
    Returns:
        {
            "success": true,
            "page": 1,
            "limit": 25,
            "total": 2994,
            "total_pages": 120,
            "transactions": [...]
        }
    """
    try:
        transactions = get_transactions()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 25))
        skip = (page - 1) * limit
        
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
        
        # Filter by supplier_id
        supplier_param = request.args.get('supplier_id')
        if supplier_param:
            query['supplier.supplier_id'] = supplier_param
        
        # Search by supplier_id or company_name
        search_param = request.args.get('search')
        if search_param:
            query['$or'] = [
                {'supplier.supplier_id': {'$regex': search_param, '$options': 'i'}},
                {'supplier.company_name': {'$regex': search_param, '$options': 'i'}}
            ]
        
        # Get total count for pagination
        total = transactions.count_documents(query)
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        # Execute query with pagination
        results = list(
            transactions.find(query)
            .sort('transaction_date', -1)  # Sort by date descending
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for transaction in results:
            transaction['_id'] = str(transaction['_id'])
        
        return jsonify({
            "success": True,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "transactions": results
        }), 200
        
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid pagination parameters"
        }), 400
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch transactions: {str(e)}"
        }), 500


@transactions_bp.route('/transactions/stats', methods=['GET'])
def get_transactions_stats():
    """
    Get statistics about transactions.
    
    Returns:
        {
            "success": true,
            "stats": {
                "total": 2994,
                "by_tier": {
                    "High Performance": 1200,
                    "Mid Performance": 1000,
                    "Low Performance": 794
                },
                "by_cluster": {
                    "0": 1200,
                    "1": 1000,
                    "2": 794
                },
                "average_scores": {...}
            }
        }
    """
    try:
        transactions = get_transactions()
        
        # Total count
        total = transactions.count_documents({})
        
        # Count by tier
        pipeline_tier = [
            {"$group": {
                "_id": "$performance_tier",
                "count": {"$sum": 1}
            }}
        ]
        tier_results = list(transactions.aggregate(pipeline_tier))
        by_tier = {item['_id']: item['count'] for item in tier_results}
        
        # Count by cluster
        pipeline_cluster = [
            {"$group": {
                "_id": "$cluster_id",
                "count": {"$sum": 1}
            }}
        ]
        cluster_results = list(transactions.aggregate(pipeline_cluster))
        by_cluster = {str(item['_id']): item['count'] for item in cluster_results}
        
        # Average scores
        pipeline_avg = [
            {"$group": {
                "_id": None,
                "overall_score": {"$avg": "$metrics.overall_score"},
                "quality_score": {"$avg": "$metrics.quality_score"},
                "delivery_reliability": {"$avg": "$metrics.delivery_reliability"},
                "cost_efficiency": {"$avg": "$metrics.cost_efficiency"},
                "customer_satisfaction": {"$avg": "$metrics.customer_satisfaction"},
                "defect_rate": {"$avg": "$metrics.defect_rate"}
            }}
        ]
        avg_results = list(transactions.aggregate(pipeline_avg))
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
        print(f"Error fetching transaction stats: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch stats: {str(e)}"
        }), 500


@transactions_bp.route('/transactions/supplier/<supplier_id>', methods=['GET'])
def get_transactions_by_supplier(supplier_id):
    """
    Get all transactions for a specific supplier.
    
    Returns:
        {
            "success": true,
            "supplier_id": "SUP_001",
            "count": 120,
            "transactions": [...]
        }
    """
    try:
        transactions = get_transactions()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 25))
        skip = (page - 1) * limit
        
        # Query by supplier_id
        query = {"supplier.supplier_id": supplier_id}
        
        # Get total count
        total = transactions.count_documents(query)
        total_pages = (total + limit - 1) // limit
        
        # Execute query
        results = list(
            transactions.find(query)
            .sort('transaction_date', -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for transaction in results:
            transaction['_id'] = str(transaction['_id'])
        
        return jsonify({
            "success": True,
            "supplier_id": supplier_id,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "transactions": results
        }), 200
        
    except Exception as e:
        print(f"Error fetching supplier transactions: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch transactions: {str(e)}"
        }), 500

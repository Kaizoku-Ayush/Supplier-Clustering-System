"""
MongoDB Schema Definitions for Supplier Clustering System
============================================================

This file defines the structure for MongoDB collections.
Three main collections:
1. companies - 25 company-level documents with aggregated performance
2. transactions - 2,994 transaction-level documents with individual records
3. recommendations - Cluster-level recommendations for each performance tier
"""

# Collection 1: Companies (25 documents)
# Purpose: Landing page - show all companies with their ensemble clustering
COMPANY_SCHEMA = {
    "supplier_id": "SUP_001",                    # Unique identifier
    "company_name": "Fowler Corp",               # Company name (if available)
    
    # Performance metrics (from supplier_aggregated_stats.csv)
    "performance": {
        "overall_score": 76.09,
        "quality_score": 79.95,
        "delivery_reliability": 74.87,
        "cost_efficiency": 65.26,
        "customer_satisfaction": 7.73,
        "defect_rate": 1.75,
        "order_volume": 37638.84
    },
    
    # Ensemble clustering result (from company_ensemble_clusters.csv)
    "cluster_id": 2,
    "performance_tier": "High Performance",  # Low Performance/Mid Performance/High Performance
    
    # Metadata
    "created_at": "2025-10-11T00:00:00Z"
}


# Collection 2: Transactions (2,994 documents)
# Purpose: Detail view - show all transaction rows with ensemble clustering
TRANSACTION_SCHEMA = {
    "transaction_date": "2015-01-01",
    
    # Supplier information
    "supplier": {
        "supplier_id": "SUP_001",
        "company_name": "Fowler Corp"
    },
    
    # Transaction metrics (from cleaned_data.csv)
    "metrics": {
        "overall_score": 79.83,
        "quality_score": 86.62,
        "delivery_reliability": 82.0,
        "cost_efficiency": 66.0,
        "customer_satisfaction": 8.0,
        "defect_rate": 1.0,
        "order_volume": 340.0
    },
    
    # Ensemble clustering result (from ensemble_clustered_suppliers.csv)
    "cluster_id": 1,
    "performance_tier": "High Performance",  # Derived from ensemble cluster
    
    # Metadata
    "created_at": "2025-10-11T00:00:00Z"
}


# Collection 3: Recommendations (3 documents - one per cluster)
# Purpose: Strategic recommendations for each ensemble cluster
# Data source: ensemble_cluster_recommendations.csv
RECOMMENDATION_SCHEMA = {
    "cluster_id": 0,
    "profile": "Premium Suppliers",
    "size": 130,
    "percentage": 4.3,
    
    # Cluster strengths and weaknesses
    "key_strengths": ["Quality Score", "Delivery Reliability"],
    "improvement_areas": ["Cost Efficiency", "Customer Satisfaction"],
    
    # Strategic recommendation
    "recommended_strategy": "Maintain partnership and leverage for critical projects",
    
    # Metadata
    "created_at": "2025-10-11T00:00:00Z"
}


# MongoDB Indexes for Performance
# These will be created after data loading
INDEXES = {
    "companies": [
        ("supplier_id", 1),  # Unique index
        ("performance.overall_score", -1),  # Sort by score (descending)
        ("performance_tier", 1),  # Filter by tier
        ("cluster_id", 1)  # Filter by cluster
    ],
    "transactions": [
        ("supplier.supplier_id", 1),  # Filter by company
        ("transaction_date", -1),  # Sort by date (descending)
        ("performance_tier", 1),  # Filter by tier
        ("cluster_id", 1)  # Filter by cluster
    ],
    "recommendations": [
        ("cluster_id", 1)  # One recommendation per cluster
    ]
}


# Database Configuration
DB_CONFIG = {
    "database_name": "supplier_clustering",
    "collections": {
        "companies": "companies",
        "transactions": "transactions",
        "recommendations": "recommendations"
    }
}


# CSV File Sources
CSV_SOURCES = {
    "companies": {
        "performance_data": "ml-pipeline/data/raw/supplier_aggregated_stats.csv",
        "clustering_data": "ml-pipeline/data/results/company_ensemble_clusters.csv"
    },
    "transactions": {
        "transaction_data": "ml-pipeline/data/processed/cleaned_data.csv",
        "clustering_data": "ml-pipeline/data/processed/ensemble_clustered_suppliers.csv"
    },
    "recommendations": {
        "recommendations_data": "ml-pipeline/data/results/ensemble_cluster_recommendations.csv"
    }
}

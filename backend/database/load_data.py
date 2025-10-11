"""
Data Loader for Supplier Clustering System
===========================================

This script loads data from CSV files into MongoDB collections.
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'models'))
from database import db_connection, get_db

# Import schemas for reference
sys.path.append(os.path.dirname(__file__))
from db_schemas import DB_CONFIG, INDEXES


class DataLoader:
    """Loads CSV data into MongoDB collections"""
    
    def __init__(self):
        """Initialize data loader with database connection"""
        self.db = get_db()
        # ml-pipeline is at the root of the project, not in backend
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml-pipeline')
        
    def clear_collections(self):
        """Clear all existing collections"""
        print("\nClearing existing collections...")
        
        for collection_name in DB_CONFIG['collections'].values():
            count = self.db[collection_name].count_documents({})
            if count > 0:
                self.db[collection_name].delete_many({})
                print(f"  Cleared {count} documents from '{collection_name}'")
        
        print("Collections cleared\n")
    
    def load_companies(self):
        """
        Load companies collection (25 documents)
        Merges data from supplier_aggregated_stats.csv and company_ensemble_clusters.csv
        """
        print("Loading Companies Collection...")
        
        # Read CSV files
        stats_path = os.path.join(self.base_path, 'data', 'raw', 'supplier_aggregated_stats.csv')
        clusters_path = os.path.join(self.base_path, 'data', 'results', 'company_ensemble_clusters.csv')
        
        stats_df = pd.read_csv(stats_path)
        clusters_df = pd.read_csv(clusters_path)
        
        # Merge on supplier_id
        merged_df = pd.merge(stats_df, clusters_df[['supplier_id', 'cluster', 'performance_tier']], 
                            on='supplier_id', how='left')
        
        print(f"   Read {len(merged_df)} companies from CSV files")
        
        # Transform to MongoDB documents
        documents = []
        for _, row in merged_df.iterrows():
            doc = {
                "supplier_id": row['supplier_id'],
                "company_name": row['supplier_id'],  # Use supplier_id as name for now
                
                # Performance metrics
                "performance": {
                    "overall_score": round(float(row['overall_score_mean']), 2),
                    "quality_score": round(float(row['quality_score_mean']), 2),
                    "delivery_reliability": round(float(row['delivery_reliability_mean']), 2),
                    "cost_efficiency": round(float(row['cost_efficiency_mean']), 2),
                    "customer_satisfaction": round(float(row['customer_satisfaction_mean']), 2),
                    "defect_rate": round(float(row['defect_rate_mean']), 2),
                    "order_volume": round(float(row['order_volume_sum']), 2)
                },
                
                # Ensemble clustering
                "cluster_id": int(row['cluster']),
                "performance_tier": row['performance_tier'],
                
                # Metadata
                "created_at": datetime.utcnow()
            }
            documents.append(doc)
        
        # Insert into MongoDB
        collection = self.db[DB_CONFIG['collections']['companies']]
        result = collection.insert_many(documents)
        
        print(f"Inserted {len(result.inserted_ids)} companies into MongoDB")
        
        # Show tier distribution
        tier_counts = merged_df['performance_tier'].value_counts()
        print(f"\n   Performance Tier Distribution:")
        for tier, count in tier_counts.items():
            print(f"   • {tier}: {count} companies")
        
        return len(documents)
    
    def load_transactions(self):
        """
        Load transactions collection (2,994 documents)
        Merges data from cleaned_data.csv and ensemble_clustered_suppliers.csv
        """
        print("\nLoading Transactions Collection...")
        
        # Read CSV files
        data_path = os.path.join(self.base_path, 'data', 'processed', 'cleaned_data.csv')
        clusters_path = os.path.join(self.base_path, 'data', 'processed', 'ensemble_clustered_suppliers.csv')
        
        data_df = pd.read_csv(data_path)
        clusters_df = pd.read_csv(clusters_path)
        
        # We'll use cluster and cluster_name from ensemble file
        # Merge on date and supplier_id
        merged_df = pd.merge(data_df, 
                            clusters_df[['date', 'supplier_id', 'cluster', 'cluster_name']], 
                            on=['date', 'supplier_id'], 
                            how='left')
        
        print(f"   Read {len(merged_df)} transactions from CSV files")
        
        # Get company performance tiers for mapping
        company_path = os.path.join(self.base_path, 'data', 'results', 'company_ensemble_clusters.csv')
        company_df = pd.read_csv(company_path)
        company_tier_map = dict(zip(company_df['supplier_id'], company_df['performance_tier']))
        
        # Transform to MongoDB documents (in batches for performance)
        documents = []
        batch_size = 500
        
        for idx, row in merged_df.iterrows():
            doc = {
                "transaction_date": row['date'],
                
                # Supplier information
                "supplier": {
                    "supplier_id": row['supplier_id'],
                    "company_name": row['company_name']
                },
                
                # Transaction metrics
                "metrics": {
                    "overall_score": round(float(row['overall_score']), 2),
                    "quality_score": round(float(row['quality_score']), 2),
                    "delivery_reliability": round(float(row['delivery_reliability']), 2),
                    "cost_efficiency": round(float(row['cost_efficiency']), 2),
                    "customer_satisfaction": round(float(row['customer_satisfaction']), 2),
                    "defect_rate": round(float(row['defect_rate']), 2),
                    "order_volume": round(float(row['order_volume']), 2)
                },
                
                # Ensemble clustering
                "cluster_id": int(row['cluster']) if pd.notna(row['cluster']) else 0,
                "performance_tier": company_tier_map.get(row['supplier_id'], "Unknown"),
                
                # Metadata
                "created_at": datetime.utcnow()
            }
            documents.append(doc)
            
            # Insert in batches for better performance
            if len(documents) >= batch_size:
                collection = self.db[DB_CONFIG['collections']['transactions']]
                collection.insert_many(documents)
                print(f"   Inserted batch: {idx + 1}/{len(merged_df)} transactions")
                documents = []
        
        # Insert remaining documents
        if documents:
            collection = self.db[DB_CONFIG['collections']['transactions']]
            collection.insert_many(documents)
        
        total_count = self.db[DB_CONFIG['collections']['transactions']].count_documents({})
        print(f"Inserted {total_count} transactions into MongoDB")
        
        return total_count
    
    def load_recommendations(self):
        """
        Load recommendations collection (3 documents)
        Reads from ensemble_cluster_recommendations.csv
        """
        print("\nLoading Recommendations Collection...")
        
        # Read CSV file
        rec_path = os.path.join(self.base_path, 'data', 'results', 'ensemble_cluster_recommendations.csv')
        rec_df = pd.read_csv(rec_path)
        
        print(f"   Read {len(rec_df)} recommendations from CSV")
        
        # Transform to MongoDB documents
        documents = []
        for _, row in rec_df.iterrows():
            doc = {
                "cluster_id": int(row['Cluster']),
                "profile": row['Profile'],
                "size": int(row['Size']),
                "percentage": float(row['Percentage'].strip('%')),
                
                # Parse comma-separated strengths and improvements
                "key_strengths": [s.strip() for s in row['Key Strengths'].split(',')],
                "improvement_areas": [s.strip() for s in row['Improvement Areas'].split(',')],
                
                "recommended_strategy": row['Recommended Strategy'],
                
                # Metadata
                "created_at": datetime.utcnow()
            }
            documents.append(doc)
        
        # Insert into MongoDB
        collection = self.db[DB_CONFIG['collections']['recommendations']]
        result = collection.insert_many(documents)
        
        print(f"Inserted {len(result.inserted_ids)} recommendations into MongoDB")
        
        return len(documents)
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        print("\nCreating database indexes...")
        
        for collection_name, index_list in INDEXES.items():
            collection = self.db[collection_name]
            
            for index_field in index_list:
                try:
                    collection.create_index([index_field])
                    print(f"   Created index on {collection_name}.{index_field[0]}")
                except Exception as e:
                    print(f"   Index creation warning for {collection_name}.{index_field[0]}: {e}")
        
        print("✅ Indexes created")
    
    def show_summary(self):
        """Display summary of loaded data"""
        
        for collection_name in DB_CONFIG['collections'].values():
            count = self.db[collection_name].count_documents({})
            print(f"{collection_name:20s}: {count:5d} documents")


def main():
    """Main function to load all data"""
    
    # Check database connection
    if not db_connection.test_connection():
        print("\nCannot connect to MongoDB. Please ensure:")
        print("   1. MongoDB is installed")
        print("   2. MongoDB service is running")
        print("   3. MongoDB is accessible at localhost:27017")
        return
    
    # Create loader instance
    loader = DataLoader()
    
    # Ask user if they want to clear existing data
    print("\nThis will load data into MongoDB.")
    response = input("Clear existing data first? (y/n): ").lower()
    if response == 'y':
        loader.clear_collections()
    
    try:
        # Load all collections
        loader.load_companies()
        loader.load_transactions()
        loader.load_recommendations()
        
        # Create indexes
        loader.create_indexes()
        
        # Show summary
        loader.show_summary()
        
    except Exception as e:
        print(f"\nError loading data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

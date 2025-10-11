"""
MongoDB Database Connection Manager
====================================

This module handles MongoDB connection and provides access to collections.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
import os

# Add the database folder to the path to import schemas
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_schemas import DB_CONFIG


class DatabaseConnection:
    """
    Manages MongoDB connection and provides access to collections.
    Implements singleton pattern to ensure only one connection exists.
    """
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if self._client is None:
            self.connect()
    
    def connect(self, host='localhost', port=27017, timeout=5000):
        """
        Connect to MongoDB server.
        """
        try:
            # Create MongoDB client with connection timeout
            connection_string = f'mongodb://{host}:{port}/'
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=timeout
            )
            
            # Test the connection
            self._client.admin.command('ping')
            
            # Get the database
            self._db = self._client[DB_CONFIG['database_name']]
            
            print(f"Successfully connected to MongoDB at {host}:{port}")
            print(f"Using database: {DB_CONFIG['database_name']}")
            return True
            
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB server not available: {e}")
            print(f"Make sure MongoDB is running on {host}:{port}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def get_database(self):
        """
        Get the MongoDB database instance.
        
        Returns:
            Database: MongoDB database object
        """
        if self._db is None:
            print("Database not connected. Attempting to connect...")
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """
        Get a specific collection from the database.
        """
        if collection_name not in DB_CONFIG['collections'].values():
            print(f"Warning: '{collection_name}' not in defined collections")
        
        db = self.get_database()
        return db[collection_name]
    
    def get_companies_collection(self):
        """Get the companies collection"""
        return self.get_collection(DB_CONFIG['collections']['companies'])
    
    def get_transactions_collection(self):
        """Get the transactions collection"""
        return self.get_collection(DB_CONFIG['collections']['transactions'])
    
    def get_recommendations_collection(self):
        """Get the recommendations collection"""
        return self.get_collection(DB_CONFIG['collections']['recommendations'])
    
    def close(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")
            self._client = None
            self._db = None
    
    def test_connection(self):
        """
        Test database connection and show collection stats.
        """
        try:
            db = self.get_database()
            
            # Get collection names
            collection_names = db.list_collection_names()
            print(f"Database: {DB_CONFIG['database_name']}")
            print(f"Collections found: {len(collection_names)}")
            
            if collection_names:
                print("\nCollection Stats:")
                for name in collection_names:
                    count = db[name].count_documents({})
                    print(f"  • {name}: {count} documents")
            else:
                print("\nNo collections found. Database is empty.")
                print("Run load_data.py to populate the database.")
            
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Global database instance (singleton)
db_connection = DatabaseConnection()


# Convenience functions for easy access
def get_db():
    """Get database instance"""
    return db_connection.get_database()


def get_companies():
    """Get companies collection"""
    return db_connection.get_companies_collection()


def get_transactions():
    """Get transactions collection"""
    return db_connection.get_transactions_collection()


def get_recommendations():
    """Get recommendations collection"""
    return db_connection.get_recommendations_collection()


# Test connection when module is imported
if __name__ == "__main__":
    print("Testing database connection...")
    db_connection.test_connection()

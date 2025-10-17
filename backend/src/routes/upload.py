"""
Upload Routes
=============
Handles CSV file upload and ensemble clustering analysis.
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import os
import sys
import datetime

# Add models and ML pipeline paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml-pipeline', 'src'))

from database import get_db

upload_bp = Blueprint('upload', __name__)

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml-pipeline', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Required columns for supplier data
REQUIRED_COLUMNS = [
    'supplier_id',
    'company_name',
    'overall_score',
    'quality_score',
    'delivery_reliability',
    'cost_efficiency',
    'customer_satisfaction',
    'defect_rate'
]


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_csv_columns(df):
    """
    Validate that CSV has all required columns.
    
    Returns:
        (bool, list): (is_valid, missing_columns)
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def perform_ensemble_clustering(df):
    """
    Perform ensemble clustering on the uploaded data.
    Uses K-Means, DBSCAN, and Hierarchical clustering with voting.
    
    Args:
        df: pandas DataFrame with supplier data
    
    Returns:
        df: DataFrame with cluster_id and performance_tier columns added
    """
    try:
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        import numpy as np
        
        # Select features for clustering
        feature_columns = [
            'overall_score',
            'quality_score',
            'delivery_reliability',
            'cost_efficiency',
            'customer_satisfaction',
            'defect_rate'
        ]
        
        # Extract features and handle missing values
        X = df[feature_columns].copy()
        
        # Fill missing values with column mean
        for col in feature_columns:
            if X[col].isnull().any():
                X[col].fillna(X[col].mean(), inplace=True)
        
        # Convert to numpy array
        X = X.values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 1. K-Means Clustering
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X_scaled)
        
        # 2. DBSCAN Clustering
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(X_scaled)
        # Map noise points (-1) to a cluster
        dbscan_labels = np.where(dbscan_labels == -1, 
                                 np.random.randint(0, 3, size=np.sum(dbscan_labels == -1)),
                                 dbscan_labels)
        
        # 3. Hierarchical Clustering
        hierarchical = AgglomerativeClustering(n_clusters=3)
        hierarchical_labels = hierarchical.fit_predict(X_scaled)
        
        # Ensemble: Voting-based approach
        # Stack all labels
        all_labels = np.vstack([kmeans_labels, dbscan_labels, hierarchical_labels])
        
        # For each sample, find the most common label (mode)
        from scipy import stats
        ensemble_labels = stats.mode(all_labels, axis=0, keepdims=False)[0]
        
        # Add cluster labels to dataframe
        df['cluster_id'] = ensemble_labels
        
        # Map cluster_id to performance_tier based on average overall_score
        cluster_means = df.groupby('cluster_id')['overall_score'].mean().sort_values(ascending=False)
        tier_mapping = {
            cluster_means.index[0]: 'High Performance',
            cluster_means.index[1]: 'Mid Performance',
            cluster_means.index[2]: 'Low Performance'
        }
        df['performance_tier'] = df['cluster_id'].map(tier_mapping)
        
        return df
        
    except Exception as e:
        print(f"Clustering error: {e}")
        raise


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload CSV file and perform ensemble clustering.
    
    Form Data:
        file: CSV file with supplier data
    
    Returns:
        {
            "success": true,
            "message": "File uploaded and analyzed successfully",
            "stats": {
                "total_records": 25,
                "clusters": {
                    "High Performance": 8,
                    "Mid Performance": 10,
                    "Low Performance": 7
                }
            },
            "results": [...]
        }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided"
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": "Only CSV files are allowed"
            }), 400
        
        # Create upload folder if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read CSV
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to read CSV: {str(e)}"
            }), 400
        
        # Validate columns
        is_valid, missing_columns = validate_csv_columns(df)
        if not is_valid:
            return jsonify({
                "success": False,
                "message": f"Missing required columns: {', '.join(missing_columns)}",
                "required_columns": REQUIRED_COLUMNS
            }), 400
        
        # Perform ensemble clustering
        try:
            df = perform_ensemble_clustering(df)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Clustering failed: {str(e)}"
            }), 500
        
        # Calculate statistics
        total_records = len(df)
        cluster_counts = df['performance_tier'].value_counts().to_dict()
        
        # Convert results to list of dictionaries
        results = df.to_dict('records')
        
        # Optionally save to database
        save_to_db = request.form.get('save_to_db', 'false').lower() == 'true'
        if save_to_db:
            db = get_db()
            uploaded_data = db['uploaded_data']
            
            # Add metadata
            for record in results:
                record['uploaded_at'] = datetime.datetime.utcnow().isoformat()
                record['filename'] = filename
            
            # Insert into database
            uploaded_data.insert_many(results)
        
        return jsonify({
            "success": True,
            "message": "File uploaded and analyzed successfully",
            "filename": filename,
            "stats": {
                "total_records": total_records,
                "clusters": cluster_counts
            },
            "results": results
        }), 200
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }), 500


@upload_bp.route('/analyze', methods=['POST'])
def analyze_data():
    """
    Analyze data that's already uploaded (alternative endpoint).
    
    Request Body:
        {
            "data": [
                {
                    "supplier_id": "SUP_001",
                    "company_name": "Company A",
                    "overall_score": 75.5,
                    ...
                },
                ...
            ]
        }
    
    Returns:
        {
            "success": true,
            "message": "Analysis complete",
            "results": [...]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Validate columns
        is_valid, missing_columns = validate_csv_columns(df)
        if not is_valid:
            return jsonify({
                "success": False,
                "message": f"Missing required columns: {', '.join(missing_columns)}",
                "required_columns": REQUIRED_COLUMNS
            }), 400
        
        # Perform clustering
        df = perform_ensemble_clustering(df)
        
        # Calculate statistics
        total_records = len(df)
        cluster_counts = df['performance_tier'].value_counts().to_dict()
        
        # Convert to list of dictionaries
        results = df.to_dict('records')
        
        return jsonify({
            "success": True,
            "message": "Analysis complete",
            "stats": {
                "total_records": total_records,
                "clusters": cluster_counts
            },
            "results": results
        }), 200
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

"""
Data Cleaning Pipeline
Cleans and prepares the supplier time-series data for analysis
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_raw_data(file_path='data/raw/raw_data.csv'):
    """Load the raw supplier data"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found: {file_path}")

    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df

def check_missing_values(df):
    """Check for missing values in the dataset"""
    print("\n" + "="*50)
    print("CHECKING FOR MISSING VALUES")
    print("="*50)

    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df)) * 100

    missing_summary = pd.DataFrame({
        'Missing Count': missing_counts,
        'Missing Percentage': missing_percentages
    })

    missing_summary = missing_summary[missing_summary['Missing Count'] > 0]

    if len(missing_summary) == 0:
        print("✓ No missing values found in the dataset")
        return df
    else:
        print("Missing values found:")
        print(missing_summary)
        return df

def check_data_types(df):
    """Check and validate data types"""
    print("\n" + "="*50)
    print("CHECKING DATA TYPES")
    print("="*50)

    print("Current data types:")
    print(df.dtypes)

    # Convert date column to datetime if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        print("✓ Converted 'date' column to datetime")

    # Ensure numeric columns are numeric
    numeric_columns = [
        'delivery_reliability', 'cost_efficiency', 'defect_rate',
        'quality_score', 'on_time_delivery_rate', 'order_volume',
        'response_time_hours', 'customer_satisfaction', 'overall_score'
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    print("✓ Validated numeric columns")
    return df

def check_duplicates(df):
    """Check for and remove duplicate rows"""
    print("\n" + "="*50)
    print("CHECKING FOR DUPLICATES")
    print("="*50)

    initial_rows = len(df)

    # Check for complete duplicates
    duplicate_count = df.duplicated().sum()
    print(f"Found {duplicate_count} complete duplicate rows")

    if duplicate_count > 0:
        df = df.drop_duplicates()
        print(f"✓ Removed {duplicate_count} duplicate rows")

    # Check for duplicates by supplier and date (should be unique)
    if 'supplier_id' in df.columns and 'date' in df.columns:
        supplier_date_duplicates = df.duplicated(subset=['supplier_id', 'date']).sum()
        if supplier_date_duplicates > 0:
            print(f"⚠ Warning: {supplier_date_duplicates} supplier-date duplicates found")
            # Remove keeping the last occurrence (most recent)
            df = df.drop_duplicates(subset=['supplier_id', 'date'], keep='last')
            print(f"✓ Removed supplier-date duplicates, keeping most recent")

    final_rows = len(df)
    print(f"Final dataset: {final_rows} rows (removed {initial_rows - final_rows} duplicates)")

    return df

def validate_ranges(df):
    """Validate that numeric values are within expected ranges"""
    print("\n" + "="*50)
    print("VALIDATING VALUE RANGES")
    print("="*50)

    validations = {
        'delivery_reliability': (0, 100),
        'cost_efficiency': (0, 100),
        'defect_rate': (0, 10),
        'quality_score': (0, 100),
        'on_time_delivery_rate': (0, 100),
        'order_volume': (0, float('inf')),
        'response_time_hours': (0, 168),  # Max 1 week
        'customer_satisfaction': (0, 10),
        'overall_score': (0, 100)
    }

    issues_found = False

    for col, (min_val, max_val) in validations.items():
        if col in df.columns:
            out_of_range = ((df[col] < min_val) | (df[col] > max_val)).sum()
            if out_of_range > 0:
                print(f"⚠ {col}: {out_of_range} values outside range [{min_val}, {max_val}]")
                issues_found = True

                # Clip values to valid range
                df[col] = df[col].clip(min_val, max_val)
                print(f"✓ Clipped {col} values to valid range")

    if not issues_found:
        print("✓ All numeric values within expected ranges")

    return df

def clean_text_columns(df):
    """Clean and standardize text columns"""
    print("\n" + "="*50)
    print("CLEANING TEXT COLUMNS")
    print("="*50)

    text_columns = ['company_name', 'industry', 'location', 'company_size']

    for col in text_columns:
        if col in df.columns:
            # Strip whitespace
            df[col] = df[col].str.strip()

            # Handle empty strings
            empty_count = (df[col] == '').sum()
            if empty_count > 0:
                print(f"⚠ {col}: {empty_count} empty strings found")
                # Fill with 'Unknown' or appropriate default
                if col == 'company_name':
                    df[col] = df[col].replace('', 'Unknown Company')
                elif col == 'industry':
                    df[col] = df[col].replace('', 'Unknown')
                elif col == 'location':
                    df[col] = df[col].replace('', 'Unknown')
                elif col == 'company_size':
                    df[col] = df[col].replace('', 'Unknown')

    print("✓ Cleaned text columns")
    return df

def final_validation(df):
    """Final validation of cleaned data"""
    print("\n" + "="*50)
    print("FINAL DATA VALIDATION")
    print("="*50)

    # Check final missing values
    final_missing = df.isnull().sum().sum()
    if final_missing == 0:
        print("✓ No missing values remaining")
    else:
        print(f"⚠ {final_missing} missing values still present")

    # Check data types
    print("Final data types:")
    print(df.dtypes.value_counts())

    # Summary statistics
    print(f"\nFinal dataset summary:")
    print(f"  - Rows: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Unique suppliers: {df['supplier_id'].nunique() if 'supplier_id' in df.columns else 'N/A'}")
    print(f"  - Date range: {df['date'].min() if 'date' in df.columns else 'N/A'} to {df['date'].max() if 'date' in df.columns else 'N/A'}")

    return df

def save_cleaned_data(df, output_path='data/processed/cleaned_data.csv'):
    """Save the cleaned dataset"""
    print("\n" + "="*50)
    print("SAVING CLEANED DATA")
    print("="*50)

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save as CSV
    df.to_csv(output_path, index=False)
    print(f"✓ Saved cleaned data to {output_path}")

    # Also save as JSON for web app
    json_path = output_path.replace('.csv', '.json')
    df.to_json(json_path, orient='records', indent=2, date_format='iso')
    print(f"✓ Saved cleaned data to {json_path}")

    return df

def main():
    """Main data cleaning pipeline"""
    print("="*60)
    print("SUPPLIER DATA CLEANING PIPELINE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    try:
        # Load raw data
        df = load_raw_data()

        # Perform cleaning steps
        df = check_missing_values(df)
        df = check_data_types(df)
        df = check_duplicates(df)
        df = validate_ranges(df)
        df = clean_text_columns(df)

        # Final validation
        df = final_validation(df)

        # Save cleaned data
        df = save_cleaned_data(df)

        print("\n" + "="*60)
        print("DATA CLEANING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The cleaned dataset is ready for preprocessing and analysis.")
        print("Next step: Run preprocessing script for feature engineering.")

    except Exception as e:
        print(f"\n❌ Error during data cleaning: {str(e)}")
        raise

if __name__ == "__main__":
    main()
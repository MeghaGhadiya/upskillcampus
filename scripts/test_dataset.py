"""
Test script to examine the dataset structure and test preprocessing
"""

import pandas as pd
import os

def examine_dataset(file_path='traffic.csv'):
    """Examine the dataset structure."""
    if not os.path.exists(file_path):
        print(f"Dataset not found at {file_path}")
        print("\nPlease download the dataset first:")
        print("1. Go to: https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data")
        print("2. Download and extract the dataset")
        print("3. Place the CSV file as 'traffic.csv' in this directory")
        return None
    
    print("=" * 60)
    print("Examining Dataset Structure")
    print("=" * 60)
    
    # Read first few rows to understand structure
    df = pd.read_csv(file_path, nrows=10)
    
    print(f"\nFile: {file_path}")
    print(f"Shape (first 10 rows): {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nSample data:")
    for col in df.columns:
        print(f"  {col}: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
    
    # Check full dataset
    print("\n" + "=" * 60)
    print("Loading full dataset...")
    df_full = pd.read_csv(file_path)
    print(f"Full dataset shape: {df_full.shape}")
    print(f"Missing values per column:")
    print(df_full.isnull().sum())
    print(f"\nDuplicate rows: {df_full.duplicated().sum()}")
    
    return df_full

if __name__ == "__main__":
    dataset = examine_dataset()
    
    if dataset is not None:
        print("\n" + "=" * 60)
        print("Testing Preprocessing...")
        print("=" * 60)
        
        from src.data_preprocessing import TrafficDataPreprocessor
        
        try:
            preprocessor = TrafficDataPreprocessor('traffic.csv')
            processed_df = preprocessor.preprocess()
            print("\nPreprocessing successful!")
            print(f"Processed dataset shape: {processed_df.shape}")
            print(f"Processed columns: {processed_df.columns.tolist()}")
        except Exception as e:
            print(f"\nError during preprocessing: {str(e)}")
            import traceback
            traceback.print_exc()


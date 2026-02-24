"""
Complete pipeline script to run the entire traffic forecasting system
with the Kaggle Smart City Traffic Patterns dataset
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dataset():
    """Check if dataset exists."""
    project_root = Path(__file__).parent.parent
    possible_paths = [
        project_root / 'traffic.csv',
        project_root / 'data' / 'traffic.csv',
        project_root / 'smart-city-traffic-patterns' / 'traffic.csv'
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"[OK] Dataset found at: {path}")
            return str(path)
    
    print("[ERROR] Dataset not found!")
    return None

def download_dataset():
    """Try to download dataset using Kaggle API."""
    print("\n" + "=" * 60)
    print("Attempting to download dataset from Kaggle...")
    print("=" * 60)
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print("Downloading dataset: utathya/smart-city-traffic-patterns")
        api.dataset_download_files('utathya/smart-city-traffic-patterns', path='.', unzip=True)
        
        # Find and rename the CSV file
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            main_file = csv_files[0]
            if main_file != 'traffic.csv':
                os.rename(main_file, 'traffic.csv')
            print("[OK] Dataset downloaded successfully!")
            return 'traffic.csv'
    except Exception as e:
        print(f"[ERROR] Error downloading: {str(e)}")
        print("\nPlease download manually:")
        print("1. Go to: https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data")
        print("2. Click 'Download' and extract the ZIP")
        print("3. Place the CSV file as 'traffic.csv' in this directory")
        return None

def run_preprocessing(data_path):
    """Run data preprocessing."""
    print("\n" + "=" * 60)
    print("Step 1: Data Preprocessing")
    print("=" * 60)
    
    from src.data_preprocessing import TrafficDataPreprocessor
    
    preprocessor = TrafficDataPreprocessor(data_path)
    processed_df = preprocessor.preprocess(date_column=None)
    project_root = Path(__file__).parent.parent
    preprocessor.save_processed_data(str(project_root / 'data' / 'traffic_processed.csv'))
    
    return processed_df

def run_eda(df):
    """Run exploratory data analysis."""
    print("\n" + "=" * 60)
    print("Step 2: Exploratory Data Analysis")
    print("=" * 60)
    
    from src.eda import TrafficEDA
    
    # Find datetime column
    datetime_col = 'DateTime'
    if datetime_col not in df.columns:
        datetime_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if datetime_cols:
            datetime_col = datetime_cols[0]
    
    eda = TrafficEDA(df, date_column=datetime_col)
    eda.generate_all_plots()
    
    print("[OK] EDA plots generated in 'plots/' directory")

def run_forecasting(df):
    """Train models and generate forecasts."""
    print("\n" + "=" * 60)
    print("Step 3: Model Training & Forecasting")
    print("=" * 60)
    
    from src.forecasting import TrafficForecaster
    
    # Find datetime column
    datetime_col = 'DateTime'
    if datetime_col not in df.columns:
        datetime_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if datetime_cols:
            datetime_col = datetime_cols[0]
    
    forecaster = TrafficForecaster(df, date_column=datetime_col, model_type='prophet')
    forecaster.train_models()
    forecaster.generate_forecasts(periods=30)
    project_root = Path(__file__).parent.parent
    forecaster.save_forecasts(str(project_root / 'forecasts'))
    
    return forecaster

def run_evaluation(df, forecaster):
    """Evaluate model performance."""
    print("\n" + "=" * 60)
    print("Step 4: Model Evaluation")
    print("=" * 60)
    
    from src.evaluation import ModelEvaluator
    
    # Find datetime column
    datetime_col = 'DateTime'
    if datetime_col not in df.columns:
        datetime_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if datetime_cols:
            datetime_col = datetime_cols[0]
    
    evaluator = ModelEvaluator(df, forecaster.models, date_column=datetime_col)
    results = evaluator.evaluate_all_models(model_type='prophet')
    project_root = Path(__file__).parent.parent
    evaluator.save_results(str(project_root / 'data' / 'evaluation_results.csv'))
    
    print("\n[OK] Evaluation complete!")
    print("\nSummary:")
    summary = evaluator.get_summary()
    print(f"  Average MAE: {summary['average_mae']:.2f}")
    print(f"  Average RMSE: {summary['average_rmse']:.2f}")
    print(f"  Average MAPE: {summary['average_mape']:.2f}%")
    
    return results

def main():
    """Run the complete pipeline."""
    print("=" * 60)
    print("Smart City Traffic Forecasting - Complete Pipeline")
    print("=" * 60)
    
    # Check for dataset
    data_path = check_dataset()
    
    if not data_path:
        print("\nDataset not found. Attempting to download...")
        data_path = download_dataset()
        
        if not data_path:
            print("\n" + "=" * 60)
            print("Please download the dataset manually and run this script again.")
            print("=" * 60)
            sys.exit(1)
    
    try:
        # Step 1: Preprocessing
        processed_df = run_preprocessing(data_path)
        
        # Step 2: EDA
        run_eda(processed_df)
        
        # Step 3: Forecasting
        forecaster = run_forecasting(processed_df)
        
        # Step 4: Evaluation
        results = run_evaluation(processed_df, forecaster)
        
        print("\n" + "=" * 60)
        print("[OK] Pipeline Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the FastAPI server: py -3 scripts/run.py")
        print("2. Open dashboard: http://localhost:8000")
        print("3. View results in:")
        print("   - plots/ - EDA visualizations")
        print("   - forecasts/ - Forecast CSV files")
        print("   - data/evaluation_results.csv - Performance metrics")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error during pipeline execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


"""
Script to download the Smart City Traffic Patterns dataset from Kaggle
"""

import os
import subprocess
import sys

def check_kaggle_installed():
    """Check if kaggle package is installed."""
    try:
        import kaggle
        return True
    except ImportError:
        return False

def install_kaggle():
    """Install kaggle package."""
    print("Installing kaggle package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "--quiet"])

def download_dataset():
    """Download the dataset from Kaggle."""
    dataset = "utathya/smart-city-traffic-patterns"
    
    print("=" * 60)
    print("Downloading Smart City Traffic Patterns Dataset")
    print("=" * 60)
    
    # Check if kaggle is installed
    if not check_kaggle_installed():
        print("\nKaggle package not found. Installing...")
        install_kaggle()
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        print(f"\nDownloading dataset: {dataset}")
        print("This may take a few minutes...")
        
        # Download dataset
        api.dataset_download_files(dataset, path='.', unzip=True)
        
        print("\n" + "=" * 60)
        print("Dataset downloaded successfully!")
        print("=" * 60)
        
        # Find the CSV file
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            print(f"\nFound CSV files: {csv_files}")
            # Rename the main file to traffic.csv if needed
            if 'traffic.csv' not in csv_files:
                main_file = csv_files[0]
                if main_file != 'traffic.csv':
                    print(f"Renaming {main_file} to traffic.csv...")
                    os.rename(main_file, 'traffic.csv')
                    print("Done!")
        
        return True
        
    except Exception as e:
        print(f"\nError downloading dataset: {str(e)}")
        print("\nAlternative: Manual Download Instructions")
        print("=" * 60)
        print("1. Go to: https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data")
        print("2. Click 'Download' button")
        print("3. Extract the ZIP file")
        print("4. Place the CSV file in this directory as 'traffic.csv'")
        print("=" * 60)
        return False

if __name__ == "__main__":
    # Check if dataset already exists
    if os.path.exists('traffic.csv'):
        print("Dataset 'traffic.csv' already exists!")
        response = input("Do you want to download again? (y/n): ")
        if response.lower() != 'y':
            print("Skipping download.")
            sys.exit(0)
    
    download_dataset()


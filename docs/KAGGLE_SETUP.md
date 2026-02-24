# Kaggle Dataset Setup Guide

## Quick Setup for Smart City Traffic Patterns Dataset

### Method 1: Automatic Download (Recommended)

1. **Set up Kaggle API credentials:**
   ```bash
   # Install kaggle package
   pip install kaggle
   
   # Create directory for credentials
   mkdir ~/.kaggle  # Linux/Mac
   # or
   mkdir C:\Users\<YourUsername>\.kaggle  # Windows
   ```

2. **Get your Kaggle API token:**
   - Go to https://www.kaggle.com/account
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`
   - Move it to `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<YourUsername>\.kaggle\kaggle.json` (Windows)

3. **Download the dataset:**
   ```bash
   python download_dataset.py
   ```

### Method 2: Manual Download

1. **Visit the dataset page:**
   - https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data

2. **Download:**
   - Click the "Download" button (you may need to sign in to Kaggle)
   - Extract the ZIP file

3. **Place the CSV file:**
   - Find the CSV file in the extracted folder
   - Rename it to `traffic.csv`
   - Place it in the project root directory

### Method 3: Run Complete Pipeline

The easiest way - this will handle everything:
```bash
python run_full_pipeline.py
```

This script will:
- Try to download the dataset automatically
- If download fails, provide manual instructions
- Run the complete preprocessing, EDA, forecasting, and evaluation pipeline

## Verify Dataset

After downloading, verify the dataset structure:
```bash
python test_dataset.py
```

This will show:
- Dataset shape and columns
- Data types
- Sample rows
- Missing values
- Test preprocessing

## Expected Dataset Structure

The Kaggle dataset should have:
- A datetime/timestamp column (auto-detected)
- Traffic count columns for junctions (auto-detected)
- Time-series data with regular intervals

The system automatically:
- Detects the datetime column
- Identifies junction columns
- Handles different column naming conventions

## Troubleshooting

**"Dataset not found" error:**
- Make sure the file is named `traffic.csv`
- Check it's in the project root directory
- Verify the file is not corrupted

**"Could not detect datetime column" error:**
- Run `python test_dataset.py` to see available columns
- Manually specify the datetime column name in the code if needed

**Kaggle API authentication error:**
- Verify `kaggle.json` is in the correct location
- Check the file has correct format (JSON with username and key)
- Make sure you're signed in to Kaggle

## Next Steps

Once the dataset is ready:
1. Run the complete pipeline: `python run_full_pipeline.py`
2. Or start the web dashboard: `python run.py`
3. Open http://localhost:8000 in your browser


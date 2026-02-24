# Complete Setup Instructions

## Step-by-Step Setup for Smart City Traffic Forecasting

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:
- pandas, numpy (data processing)
- matplotlib, seaborn (visualization)
- prophet (forecasting)
- fastapi, uvicorn (backend API)
- kaggle (dataset download)

### Step 2: Download the Dataset

**Option A: Using Kaggle API (Easiest)**

1. Get Kaggle API credentials:
   - Go to https://www.kaggle.com/account
   - Click "Create New API Token"
   - Save the downloaded `kaggle.json` file
   - Place it in:
     - Windows: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
     - Linux/Mac: `~/.kaggle/kaggle.json`

2. Download dataset:
   ```bash
   python download_dataset.py
   ```

**Option B: Manual Download**

1. Visit: https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data
2. Click "Download" (sign in if needed)
3. Extract the ZIP file
4. Find the CSV file and rename it to `traffic.csv`
5. Place it in the project root directory

**Option C: Run Complete Pipeline (Recommended)**

This will try to download automatically and run everything:
```bash
python run_full_pipeline.py
```

### Step 3: Verify Dataset

Check if the dataset is correctly formatted:
```bash
python test_dataset.py
```

This will show:
- Dataset structure
- Column names
- Data types
- Sample data
- Test preprocessing

### Step 4: Run the System

**Option 1: Complete Pipeline (All-in-One)**
```bash
python run_full_pipeline.py
```

This runs:
- Data preprocessing
- EDA visualization
- Model training
- Forecast generation
- Model evaluation

**Option 2: Web Dashboard (Interactive)**
```bash
python run.py
```

Then open: http://localhost:8000

Use the dashboard buttons to:
1. Load & Preprocess Data
2. Generate EDA Plots
3. Train Models
4. Generate Forecasts
5. Evaluate Models

### Step 5: View Results

After running the pipeline, check:

- **EDA Plots**: `plots/` directory
  - `traffic_trends.png`
  - `working_days_vs_holidays.png`
  - `peak_hours.png`
  - `seasonal_patterns.png`
  - `weekday_patterns.png`

- **Forecasts**: `forecasts/` directory
  - CSV files with 30-day forecasts for each junction

- **Metrics**: `data/evaluation_results.csv`
  - MAE, RMSE, MAPE for each junction

- **Processed Data**: `data/traffic_processed.csv`
  - Cleaned and preprocessed dataset

## Quick Start (All Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download dataset (choose one method)
python download_dataset.py
# OR manually download and place as traffic.csv

# 3. Run complete pipeline
python run_full_pipeline.py

# 4. Start web dashboard
python run.py
# Open http://localhost:8000
```

## Troubleshooting

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`

**"Dataset not found"**
- Make sure `traffic.csv` is in the project root
- Check the file name is exactly `traffic.csv`

**"Could not detect datetime column"**
- Run: `python test_dataset.py` to see available columns
- The system auto-detects datetime columns, but you can manually specify if needed

**Kaggle API errors**
- Verify `kaggle.json` is in the correct location
- Check you're signed in to Kaggle
- Try manual download instead

**Port already in use**
- Change port in `run.py` or use: `uvicorn main:app --port 8001`

## Expected Output

After successful execution, you should have:

✅ Cleaned dataset ready for modeling
✅ EDA visualizations showing traffic patterns
✅ Trained forecasting models for each junction
✅ 30-day traffic forecasts
✅ Performance metrics (MAE, RMSE, MAPE)
✅ Interactive web dashboard

## Need Help?

- Check `README.md` for detailed documentation
- See `KAGGLE_SETUP.md` for Kaggle-specific setup
- See `QUICKSTART.md` for quick reference
- See `DATASET_FORMAT.md` for dataset structure details


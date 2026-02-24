# How to Run the Smart City Traffic Forecasting System

## Quick Start Guide

### Step 1: Install Dependencies

First, make sure all required Python packages are installed:

```bash
py -3 -m pip install -r requirements.txt
```

Or if `py -3` doesn't work, try:
```bash
python -m pip install -r requirements.txt
```

### Step 2: Verify Dataset

Make sure `traffic.csv` is in the project root directory:
```bash
dir traffic.csv
```

If the file doesn't exist, download it from:
https://www.kaggle.com/datasets/utathya/smart-city-traffic-patterns/data

### Step 3: Choose Your Method

You have **two options** to run the system:

---

## Option A: Run Complete Pipeline (Recommended for First Time)

This runs everything automatically - preprocessing, EDA, training, forecasting, and evaluation.

```bash
py -3 run_full_pipeline.py
```

**What this does:**
1. ✅ Loads and preprocesses the dataset
2. ✅ Generates EDA visualizations
3. ✅ Trains forecasting models (takes 5-10 minutes)
4. ✅ Generates 30-day forecasts
5. ✅ Evaluates model performance

**Output:**
- `data/traffic_processed.csv` - Cleaned data
- `plots/*.png` - EDA visualizations
- `models/*.pkl` - Trained models
- `forecasts/*.csv` - Forecast results
- `data/evaluation_results.csv` - Performance metrics

---

## Option B: Run Web Dashboard (Interactive)

This starts a web server where you can use buttons to control each step.

### Step 1: Start the Server

```bash
py -3 run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Open the Dashboard

Open your web browser and go to:
```
http://localhost:8000
```

Or simply:
```
http://127.0.0.1:8000
```

### Step 3: Use the Dashboard Buttons

Click the buttons **in this order**:

1. **Load & Preprocess Data**
   - Loads and cleans the dataset
   - Takes ~30 seconds

2. **Generate EDA Plots**
   - Creates exploratory visualizations
   - Takes ~1 minute

3. **Train Models**
   - Trains forecasting models for all junctions
   - ⚠️ Takes 5-10 minutes (be patient!)

4. **Generate Forecasts**
   - Creates 30-day traffic forecasts
   - Takes ~1 minute

5. **Evaluate Models**
   - Calculates MAE, RMSE, MAPE metrics
   - Takes ~1 minute

6. **Refresh Dashboard**
   - Reloads all data and displays results

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

**Solution:**
```bash
py -3 -m pip install -r requirements.txt
```

### "Dataset not found"

**Solution:**
- Make sure `traffic.csv` is in the project root directory
- Check the file name is exactly `traffic.csv` (case-sensitive)

### "Port 8000 already in use"

**Solution:**
- Close other applications using port 8000
- Or change the port in `run.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)
  ```
- Then access: `http://localhost:8001`

### "Cannot connect to server"

**Solution:**
- Make sure the server is running (`py -3 run.py`)
- Check the server is on port 8000
- Try `http://127.0.0.1:8000` instead of `localhost`

### Buttons not working

**Solution:**
- Check browser console (F12) for errors
- Make sure server is running
- Try refreshing the page (F5)
- Check that CORS is enabled (it should be by default)

### Models taking too long

**Solution:**
- This is normal! Training takes 5-10 minutes
- Be patient and don't close the browser
- Check the status message for progress

---

## Expected Results

After running the complete pipeline or using all dashboard buttons, you should have:

### Files Created:
- ✅ `data/traffic_processed.csv` - Processed dataset
- ✅ `plots/traffic_trends.png` - Traffic trends over time
- ✅ `plots/working_days_vs_holidays.png` - Holiday comparison
- ✅ `plots/peak_hours.png` - Peak hours analysis
- ✅ `plots/seasonal_patterns.png` - Seasonal trends
- ✅ `plots/weekday_patterns.png` - Day of week patterns
- ✅ `models/Junction_1_prophet.pkl` - Trained models (4 files)
- ✅ `forecasts/Junction_1_forecast.csv` - Forecasts (4 files)
- ✅ `data/evaluation_results.csv` - Performance metrics

### Dashboard Shows:
- 📊 Model performance metrics (MAE, RMSE, MAPE)
- 🔮 Interactive forecast charts for each junction
- 📈 EDA visualization plots

---

## Quick Commands Reference

```bash
# Install dependencies
py -3 -m pip install -r requirements.txt

# Run complete pipeline
py -3 run_full_pipeline.py

# Start web dashboard
py -3 run.py

# Test dataset structure
py -3 test_dataset.py

# Check if server is running
# Open: http://localhost:8000/api
```

---

## Next Steps

1. **View Results:**
   - Check `plots/` folder for visualizations
   - Check `forecasts/` folder for CSV forecast files
   - Check `data/evaluation_results.csv` for metrics

2. **Use the Dashboard:**
   - Interactive charts and visualizations
   - Real-time updates
   - Easy to use interface

3. **Customize:**
   - Adjust forecast period (default: 30 days)
   - Change model type (Prophet/ARIMA)
   - Modify holiday detection

---

## Need Help?

- Check `README.md` for detailed documentation
- Check `SETUP_INSTRUCTIONS.md` for setup help
- Check `QUICKSTART.md` for quick reference
- Check browser console (F12) for JavaScript errors
- Check server terminal for Python errors

---

**Happy Forecasting! 🚦📊**


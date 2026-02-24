# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Dataset
1. Download from: https://drive.google.com/file/d/1y61cDyuO9Zrp1fSchWcAmCxk0B6SMx7X/view?usp=sharing
2. Save as `traffic.csv` in the project root

### Step 3: Start the Server
```bash
python run.py
```

### Step 4: Open Dashboard
Open your browser and go to:
```
http://localhost:8000
```

### Step 5: Use the Dashboard
Click the buttons in this order:
1. **Load & Preprocess Data** - Loads and cleans your dataset
2. **Generate EDA Plots** - Creates exploratory visualizations
3. **Train Models** - Trains forecasting models (takes a few minutes)
4. **Generate Forecasts** - Creates 30-day forecasts
5. **Evaluate Models** - Calculates performance metrics

## 📊 What You'll See

- **Metrics Section**: MAE, RMSE, and MAPE for each junction
- **Forecasts Section**: Interactive charts showing 30-day traffic forecasts
- **EDA Section**: Visualizations of traffic patterns, peak hours, and holiday effects

## 🎯 Expected Results

After completing all steps, you should have:
- ✅ Cleaned dataset in `data/traffic_processed.csv`
- ✅ Trained models in `models/` directory
- ✅ Forecast plots in `forecasts/` directory
- ✅ EDA visualizations in `plots/` directory
- ✅ Performance metrics displayed in the dashboard

## ⚠️ Troubleshooting

**Dataset not loading?**
- Check that `traffic.csv` is in the project root
- Verify the file has a `DateTime` column

**Models taking too long?**
- This is normal for large datasets (can take 5-10 minutes)
- Be patient, especially for Prophet models

**Dashboard not showing data?**
- Make sure you clicked all buttons in order
- Check browser console for errors (F12)
- Verify the API server is running

## 💡 Tips

- Start with a smaller dataset subset for testing
- Check the API documentation at `http://localhost:8000/docs`
- All outputs are saved automatically for later use


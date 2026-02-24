# Smart City Traffic Forecasting System

A comprehensive traffic forecasting system for predicting traffic peaks at four city junctions, with special consideration for holidays and special occasions.

## 📁 Project Structure

```
internship_project/
├── src/                    # Backend source code
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── data_preprocessing.py
│   ├── eda.py
│   ├── forecasting.py
│   └── evaluation.py
├── static/                 # Frontend files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── scripts/                # Utility scripts
│   ├── run.py              # Start web server
│   ├── run_full_pipeline.py
│   ├── download_dataset.py
│   └── test_dataset.py
├── docs/                   # Documentation
│   ├── README.md           # Detailed documentation
│   ├── HOW_TO_RUN.md       # Running instructions
│   ├── SETUP_INSTRUCTIONS.md
│   ├── QUICKSTART.md
│   ├── KAGGLE_SETUP.md
│   └── DATASET_FORMAT.md
├── data/                   # Processed data (auto-generated)
├── models/                 # Trained models (auto-generated)
├── plots/                  # EDA visualizations (auto-generated)
├── forecasts/              # Forecast results (auto-generated)
├── requirements.txt        # Python dependencies
├── .gitignore
└── traffic.csv            # Dataset (download from Kaggle)
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
py -3 -m pip install -r requirements.txt
```

### 2. Download Dataset
Place `traffic.csv` in the project root, or use:
```bash
py -3 scripts/download_dataset.py
```

### 3. Run the System

**Option A: Web Dashboard (Recommended)**
```bash
py -3 scripts/run.py
```
Then open: http://localhost:8000

**Option B: Complete Pipeline**
```bash
py -3 scripts/run_full_pipeline.py
```

## 📚 Documentation

- **Quick Start**: See `docs/QUICKSTART.md`
- **How to Run**: See `docs/HOW_TO_RUN.md`
- **Setup Guide**: See `docs/SETUP_INSTRUCTIONS.md`
- **Kaggle Setup**: See `docs/KAGGLE_SETUP.md`
- **Dataset Format**: See `docs/DATASET_FORMAT.md`
- **Full Documentation**: See `docs/README.md`

## 🎯 Features

- ✅ Data preprocessing and cleaning
- ✅ Exploratory Data Analysis (EDA)
- ✅ Time-series forecasting (Prophet/ARIMA)
- ✅ Model evaluation (MAE, RMSE, MAPE)
- ✅ Interactive web dashboard
- ✅ RESTful API backend

## 📊 Output

After running, check:
- `data/traffic_processed.csv` - Cleaned dataset
- `plots/*.png` - EDA visualizations
- `models/*.pkl` - Trained models
- `forecasts/*.csv` - Forecast results
- `data/evaluation_results.csv` - Performance metrics

## 🛠️ Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## 📝 License

This project is created for educational and government planning purposes.

---

For detailed information, see the `docs/` directory.

# Project Structure

This document explains the organization of the Smart City Traffic Forecasting project.

## 📂 Directory Structure

```
internship_project/
│
├── src/                          # Backend source code
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # FastAPI application and API endpoints
│   ├── data_preprocessing.py     # Data loading and preprocessing
│   ├── eda.py                    # Exploratory Data Analysis
│   ├── forecasting.py            # Forecasting models (Prophet/ARIMA)
│   └── evaluation.py             # Model evaluation metrics
│
├── static/                       # Frontend web application
│   ├── index.html                # Dashboard HTML
│   ├── style.css                 # Dashboard styles
│   └── app.js                    # Dashboard JavaScript
│
├── scripts/                      # Utility and execution scripts
│   ├── run.py                    # Start FastAPI web server
│   ├── run_full_pipeline.py      # Run complete pipeline
│   ├── download_dataset.py       # Download dataset from Kaggle
│   └── test_dataset.py           # Test dataset structure
│
├── docs/                         # Documentation
│   ├── README.md                 # Detailed project documentation
│   ├── HOW_TO_RUN.md             # Running instructions
│   ├── SETUP_INSTRUCTIONS.md     # Setup guide
│   ├── QUICKSTART.md             # Quick start guide
│   ├── KAGGLE_SETUP.md           # Kaggle dataset setup
│   └── DATASET_FORMAT.md         # Dataset format guide
│
├── data/                         # Data directory (auto-generated)
│   ├── traffic_processed.csv     # Processed dataset
│   └── evaluation_results.csv    # Model evaluation results
│
├── models/                       # Trained models (auto-generated)
│   └── Junction_*_prophet.pkl    # Saved model files
│
├── plots/                        # EDA visualizations (auto-generated)
│   ├── traffic_trends.png
│   ├── working_days_vs_holidays.png
│   ├── peak_hours.png
│   ├── seasonal_patterns.png
│   └── weekday_patterns.png
│
├── forecasts/                    # Forecast results (auto-generated)
│   └── Junction_*_forecast.csv   # Forecast CSV files
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── README.md                     # Main project README
├── PROJECT_STRUCTURE.md          # This file
└── traffic.csv                   # Dataset (download from Kaggle)
```

## 📋 File Descriptions

### Source Code (`src/`)

- **main.py**: FastAPI backend server with REST API endpoints
- **data_preprocessing.py**: Handles data loading, cleaning, and feature engineering
- **eda.py**: Generates exploratory data analysis visualizations
- **forecasting.py**: Implements Prophet and ARIMA forecasting models
- **evaluation.py**: Calculates MAE, RMSE, and MAPE metrics

### Frontend (`static/`)

- **index.html**: Main dashboard HTML structure
- **style.css**: CSS styling for the dashboard
- **app.js**: JavaScript for API calls and interactive features

### Scripts (`scripts/`)

- **run.py**: Starts the FastAPI web server
- **run_full_pipeline.py**: Runs the complete pipeline automatically
- **download_dataset.py**: Downloads dataset from Kaggle
- **test_dataset.py**: Tests dataset structure and preprocessing

### Documentation (`docs/`)

- **README.md**: Comprehensive project documentation
- **HOW_TO_RUN.md**: Step-by-step running instructions
- **SETUP_INSTRUCTIONS.md**: Installation and setup guide
- **QUICKSTART.md**: Quick reference guide
- **KAGGLE_SETUP.md**: Kaggle dataset download instructions
- **DATASET_FORMAT.md**: Expected dataset structure

### Output Directories

- **data/**: Contains processed datasets and evaluation results
- **models/**: Stores trained forecasting models
- **plots/**: Contains EDA visualization images
- **forecasts/**: Contains forecast CSV files

## 🔄 Workflow

1. **Data**: Place `traffic.csv` in project root
2. **Preprocessing**: `src/data_preprocessing.py` processes the data
3. **EDA**: `src/eda.py` generates visualizations → `plots/`
4. **Training**: `src/forecasting.py` trains models → `models/`
5. **Forecasting**: Generates predictions → `forecasts/`
6. **Evaluation**: `src/evaluation.py` calculates metrics → `data/`

## 🚀 Running the Project

### Web Dashboard
```bash
py -3 scripts/run.py
```

### Complete Pipeline
```bash
py -3 scripts/run_full_pipeline.py
```

## 📝 Notes

- All output directories are auto-generated when scripts run
- Keep `traffic.csv` in the project root for easy access
- Documentation is organized in `docs/` for easy reference
- Source code is separated from scripts for better organization


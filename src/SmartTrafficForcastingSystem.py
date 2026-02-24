"""
FastAPI Backend for Traffic Forecasting System
Provides REST API endpoints for forecasts, metrics, and visualizations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import pandas as pd
import numpy as np
import os
import pickle
import json
from datetime import datetime, timedelta
from typing import Optional
import base64

# Import modules (using absolute imports for better compatibility)
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_preprocessing import TrafficDataPreprocessor
from src.forecasting import TrafficForecaster
from src.evaluation import ModelEvaluator
from src.eda import TrafficEDA

app = FastAPI(title="Smart City Traffic Forecasting API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store processed data and models
processed_df = None
models = {}
forecasts = {}
evaluation_results = {}
forecaster = None

# Directories (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
MODELS_DIR = PROJECT_ROOT / 'models'
PLOTS_DIR = PROJECT_ROOT / 'plots'
FORECASTS_DIR = PROJECT_ROOT / 'forecasts'


# Mount static files
static_path = PROJECT_ROOT / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    print(f"Warning: Static directory not found at {static_path}")

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    global processed_df, models, forecasts, evaluation_results
    
    # Create directories
    for dir_path in [DATA_DIR, MODELS_DIR, PLOTS_DIR, FORECASTS_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    print("API started. Use /load-data endpoint to load and process data.")
    print("Frontend available at: http://localhost:8000/static/index.html")


@app.get("/")
async def root():
    """Root endpoint - redirects to dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Smart City Traffic Forecasting API",
        "endpoints": {
            "load_data": "/load-data",
            "train_models": "/train-models",
            "generate_forecasts": "/generate-forecasts",
            "evaluate_models": "/evaluate-models",
            "get_forecasts": "/forecasts/{junction}",
            "get_all_forecasts": "/forecasts",
            "get_metrics": "/metrics",
            "get_plots": "/plots/{plot_name}"
        }
    }


@app.post("/load-data")
async def load_and_preprocess_data(data_path: Optional[str] = None):
    """Load and preprocess the traffic dataset."""
    global processed_df
    
    try:
        # Default data path
        if data_path is None:
            data_path = PROJECT_ROOT / 'traffic.csv'
            if not data_path.exists():
                # Try in data directory
                data_path = DATA_DIR / 'traffic.csv'
            data_path = str(data_path)
        
        if not os.path.exists(data_path):
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found at {data_path}. Please upload the dataset first."
            )
        
        # Preprocess data (auto-detect datetime column)
        preprocessor = TrafficDataPreprocessor(data_path)
        processed_df = preprocessor.preprocess(date_column=None)
        
        # Save processed data
        DATA_DIR.mkdir(exist_ok=True)
        output_path = DATA_DIR / 'traffic_processed.csv'
        processed_df.to_csv(str(output_path), index=False)
        
        # Find datetime column for date range
        datetime_col = 'DateTime'
        if datetime_col not in processed_df.columns:
            datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if datetime_cols:
                datetime_col = datetime_cols[0]
        
        date_range = {}
        if datetime_col in processed_df.columns:
            date_range = {
                "start": str(processed_df[datetime_col].min()),
                "end": str(processed_df[datetime_col].max())
            }
        
        return {
            "status": "success",
            "message": "Data loaded and preprocessed successfully",
            "shape": processed_df.shape,
            "columns": processed_df.columns.tolist(),
            "date_range": date_range
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-eda")
async def generate_eda_plots():
    """Generate EDA visualizations."""
    global processed_df
    
    if processed_df is None:
        # Try to load processed data
        processed_path = DATA_DIR / 'traffic_processed.csv'
        if processed_path.exists():
            try:
                processed_df = pd.read_csv(str(processed_path))
                # Find datetime column
                datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                if datetime_cols:
                    processed_df[datetime_cols[0]] = pd.to_datetime(processed_df[datetime_cols[0]])
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error loading processed data: {str(e)}. Please use /load-data endpoint first."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="No data loaded. Please use /load-data endpoint first."
            )
    
    try:
        # Find datetime column
        datetime_col = 'DateTime'
        if datetime_col not in processed_df.columns:
            datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if datetime_cols:
                datetime_col = datetime_cols[0]
        
        eda = TrafficEDA(processed_df, date_column=datetime_col)
        eda.generate_all_plots()
        
        return {
            "status": "success",
            "message": "EDA plots generated successfully",
            "plots_dir": PLOTS_DIR
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train-models")
async def train_forecasting_models(model_type: str = "prophet"):
    """Train forecasting models for all junctions."""
    global processed_df, models, forecaster
    
    if processed_df is None:
        # Try to load processed data
        processed_path = DATA_DIR / 'traffic_processed.csv'
        if processed_path.exists():
            try:
                processed_df = pd.read_csv(str(processed_path))
                # Find datetime column
                datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                if datetime_cols:
                    processed_df[datetime_cols[0]] = pd.to_datetime(processed_df[datetime_cols[0]])
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error loading processed data: {str(e)}. Please use /load-data endpoint first."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="No data loaded. Please use /load-data endpoint first."
            )
    
    try:
        # Find datetime column
        datetime_col = 'DateTime'
        if datetime_col not in processed_df.columns:
            datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if datetime_cols:
                datetime_col = datetime_cols[0]
        
        forecaster = TrafficForecaster(processed_df, date_column=datetime_col, model_type=model_type)
        models = forecaster.train_models()
        
        return {
            "status": "success",
            "message": f"Models trained successfully using {model_type}",
            "junctions": list(models.keys()),
            "model_count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-forecasts")
async def generate_forecasts(periods: int = 30):
    """Generate traffic forecasts for the next N days."""
    global forecaster, forecasts
    
    if forecaster is None or not forecaster.models:
        raise HTTPException(
            status_code=400,
            detail="No models trained. Please use /train-models endpoint first."
        )
    
    try:
        forecasts = forecaster.generate_forecasts(periods=periods)
        FORECASTS_DIR.mkdir(exist_ok=True)
        forecaster.save_forecasts(str(FORECASTS_DIR))
        
        # Convert forecasts to JSON-serializable format
        forecasts_json = {}
        for junction, forecast_df in forecasts.items():
            forecasts_json[junction] = {
                'dates': forecast_df['date'].astype(str).tolist(),
                'forecast': forecast_df['forecast'].tolist(),
                'lower_bound': forecast_df['lower_bound'].tolist(),
                'upper_bound': forecast_df['upper_bound'].tolist()
            }
        
        return {
            "status": "success",
            "message": f"Forecasts generated for next {periods} days",
            "forecasts": forecasts_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate-models")
async def evaluate_models(model_type: str = "prophet"):
    """Evaluate model performance."""
    global processed_df, models, evaluation_results
    
    if not models:
        raise HTTPException(
            status_code=400,
            detail="No models available. Please train models first."
        )
    
    if processed_df is None:
        processed_path = DATA_DIR / 'traffic_processed.csv'
        if processed_path.exists():
            try:
                processed_df = pd.read_csv(str(processed_path))
                # Find datetime column
                datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                if datetime_cols:
                    processed_df[datetime_cols[0]] = pd.to_datetime(processed_df[datetime_cols[0]])
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error loading processed data: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="No data available for evaluation."
            )
    
    try:
        # Find datetime column
        datetime_col = 'DateTime'
        if datetime_col not in processed_df.columns:
            datetime_cols = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if datetime_cols:
                datetime_col = datetime_cols[0]
        
        evaluator = ModelEvaluator(processed_df, models, date_column=datetime_col)
        evaluation_results = evaluator.evaluate_all_models(model_type=model_type)
        DATA_DIR.mkdir(exist_ok=True)
        evaluator.save_results(str(DATA_DIR / 'evaluation_results.csv'))
        
        # Prepare results for JSON response
        results_json = {}
        for junction, metrics in evaluation_results.items():
            results_json[junction] = {
                'mae': float(metrics['mae']),
                'rmse': float(metrics['rmse']),
                'mape': float(metrics['mape']) if not np.isnan(metrics['mape']) else None
            }
        
        summary = evaluator.get_summary()
        
        return {
            "status": "success",
            "message": "Models evaluated successfully",
            "metrics": results_json,
            "summary": {
                "average_mae": float(summary['average_mae']),
                "average_rmse": float(summary['average_rmse']),
                "average_mape": float(summary['average_mape']) if not np.isnan(summary['average_mape']) else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecasts")
async def get_all_forecasts():
    """Get forecasts for all junctions."""
    global forecasts
    
    if not forecasts:
        # Try to load from files
        forecasts = {}
        if FORECASTS_DIR.exists():
            for file in FORECASTS_DIR.glob('*_forecast.csv'):
                junction = file.stem.replace('_forecast', '')
                try:
                    df = pd.read_csv(str(file))
                    forecasts[junction] = df
                except Exception as e:
                    print(f"Error loading forecast file {file}: {e}")
                    continue
    
    if not forecasts:
        # Return empty forecasts instead of error
        return {
            "status": "success",
            "forecasts": {},
            "message": "No forecasts available. Please generate forecasts first."
        }
    
    # Convert to JSON
    forecasts_json = {}
    for junction, forecast_df in forecasts.items():
        if isinstance(forecast_df, pd.DataFrame):
            forecasts_json[junction] = {
                'dates': forecast_df['date'].astype(str).tolist(),
                'forecast': forecast_df['forecast'].tolist(),
                'lower_bound': forecast_df['lower_bound'].tolist() if 'lower_bound' in forecast_df.columns else None,
                'upper_bound': forecast_df['upper_bound'].tolist() if 'upper_bound' in forecast_df.columns else None
            }
    
    return {
        "status": "success",
        "forecasts": forecasts_json
    }


@app.get("/forecasts/{junction}")
async def get_forecast_for_junction(junction: str):
    """Get forecast for a specific junction."""
    global forecasts
    
    if not forecasts:
        # Try to load from file
        forecast_path = FORECASTS_DIR / f'{junction}_forecast.csv'
        if forecast_path.exists():
            try:
                forecast_df = pd.read_csv(str(forecast_path))
                forecasts[junction] = forecast_df
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error loading forecast for {junction}: {str(e)}"
                )
    
    if junction not in forecasts:
        raise HTTPException(
            status_code=404,
            detail=f"No forecast found for junction {junction}. Please generate forecasts first."
        )
    
    forecast_df = forecasts[junction]
    if isinstance(forecast_df, pd.DataFrame):
        return {
            "status": "success",
            "junction": junction,
            "forecast": {
                'dates': forecast_df['date'].astype(str).tolist(),
                'forecast': forecast_df['forecast'].tolist(),
                'lower_bound': forecast_df['lower_bound'].tolist() if 'lower_bound' in forecast_df.columns else None,
                'upper_bound': forecast_df['upper_bound'].tolist() if 'upper_bound' in forecast_df.columns else None
            }
        }
    
    return forecasts[junction]


@app.get("/metrics")
async def get_evaluation_metrics():
    """Get evaluation metrics for all models."""
    global evaluation_results
    
    if not evaluation_results:
        # Try to load from file
        results_path = DATA_DIR / 'evaluation_results.csv'
        if results_path.exists():
            try:
                results_df = pd.read_csv(str(results_path))
                evaluation_results = {}
                for _, row in results_df.iterrows():
                    evaluation_results[row['Junction']] = {
                        'mae': float(row['MAE']),
                        'rmse': float(row['RMSE']),
                        'mape': float(row['MAPE']) if not pd.isna(row['MAPE']) else None
                    }
            except Exception as e:
                # If file exists but can't be read, return empty
                evaluation_results = {}
        else:
            # Return empty results instead of error
            return {
                "status": "success",
                "metrics": {},
                "summary": {
                    "average_mae": None,
                    "average_rmse": None,
                    "average_mape": None
                },
                "message": "No evaluation results available. Please evaluate models first."
            }
    
    # Calculate summary
    mae_values = [v['mae'] for v in evaluation_results.values() if v['mae'] is not None]
    rmse_values = [v['rmse'] for v in evaluation_results.values() if v['rmse'] is not None]
    mape_values = [v['mape'] for v in evaluation_results.values() if v['mape'] is not None and v['mape'] is not None]
    
    return {
        "status": "success",
        "metrics": evaluation_results,
        "summary": {
            "average_mae": float(np.mean(mae_values)) if mae_values else None,
            "average_rmse": float(np.mean(rmse_values)) if rmse_values else None,
            "average_mape": float(np.mean(mape_values)) if mape_values else None
        }
    }


@app.get("/plots/{plot_name}")
async def get_plot(plot_name: str):
    """Get a specific plot image."""
    plot_path = PLOTS_DIR / plot_name
    
    if not plot_path.exists():
        # Return a placeholder or informative error
        raise HTTPException(
            status_code=404,
            detail=f"Plot '{plot_name}' not found. Please generate EDA plots first using the 'Generate EDA Plots' button."
        )
    
    return FileResponse(str(plot_path), media_type="image/png")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "data_loaded": processed_df is not None,
        "models_trained": len(models) > 0,
        "forecasts_available": len(forecasts) > 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


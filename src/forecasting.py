"""
Traffic Forecasting Module
Uses Prophet and ARIMA for time-series forecasting.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import warnings
import os
import pickle
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')


class TrafficForecaster:
    """Forecast traffic for multiple junctions."""
    
    def __init__(self, df, date_column='DateTime', model_type='prophet'):
        """
        Initialize forecaster.
        
        Args:
            df: Preprocessed DataFrame
            date_column: Name of the datetime column
            model_type: 'prophet' or 'arima'
        """
        self.df = df.copy()
        self.date_column = date_column
        self.model_type = model_type.lower()
        self.models = {}
        self.forecasts = {}
        # Use project root for models directory
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        self.models_dir = project_root / 'models'
        self.models_dir.mkdir(exist_ok=True)
    
    def get_junction_columns(self):
        """Get column names for traffic junctions."""
        junction_cols = [col for col in self.df.columns 
                        if 'junction' in col.lower() or 'traffic' in col.lower() 
                        or col.isdigit() or 'Junction' in col]
        
        if not junction_cols:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = ['hour', 'day', 'month', 'day_of_week', 'is_weekend', 
                          'is_holiday', 'is_special_occasion', 'is_holiday_or_special']
            junction_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        return junction_cols[:4] if len(junction_cols) >= 4 else junction_cols
    
    def prepare_prophet_data(self, junction_col):
        """Prepare data in Prophet format."""
        prophet_df = pd.DataFrame({
            'ds': self.df[self.date_column],
            'y': self.df[junction_col]
        })
        
        # Add holiday regressor if available
        if 'is_holiday_or_special' in self.df.columns:
            prophet_df['holiday'] = self.df['is_holiday_or_special']
        
        return prophet_df.dropna()
    
    def train_prophet_model(self, junction_col):
        """Train Prophet model for a junction."""
        print(f"Training Prophet model for {junction_col}...")
        
        prophet_df = self.prepare_prophet_data(junction_col)
        
        # Remove any infinite or very large values
        prophet_df = prophet_df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Ensure y values are positive (Prophet requires positive values)
        prophet_df['y'] = prophet_df['y'].clip(lower=0.1)
        
        try:
            # Initialize Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,  # Disable daily for hourly data
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05
            )
            
            # Add holiday regressor if available
            if 'holiday' in prophet_df.columns:
                model.add_regressor('holiday')
            
            # Fit model
            model.fit(prophet_df[['ds', 'y']])
            
            return model
        except Exception as e:
            print(f"  Warning: Prophet failed with error: {str(e)}")
            print(f"  Falling back to ARIMA model...")
            # Fallback to ARIMA if Prophet fails
            return self.train_arima_model(junction_col)
    
    def train_arima_model(self, junction_col, order=(5, 1, 0)):
        """Train ARIMA model for a junction."""
        print(f"Training ARIMA model for {junction_col}...")
        
        # Prepare time series data
        ts_data = self.df.set_index(self.date_column)[junction_col].dropna()
        
        # Fit ARIMA model
        model = ARIMA(ts_data, order=order)
        fitted_model = model.fit()
        
        return fitted_model
    
    def train_models(self):
        """Train models for all junctions."""
        print("=" * 50)
        print("Training Forecasting Models")
        print("=" * 50)
        
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            print("No junction columns found!")
            return
        
        for junction in junction_cols:
            try:
                if self.model_type == 'prophet':
                    model = self.train_prophet_model(junction)
                else:
                    model = self.train_arima_model(junction)
                
                self.models[junction] = model
                
                # Save model
                model_path = self.models_dir / f'{junction}_{self.model_type}.pkl'
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                print(f"Model saved: {model_path}")
                
            except Exception as e:
                print(f"Error training model for {junction}: {str(e)}")
                continue
        
        print(f"\nTrained {len(self.models)} models")
        return self.models
    
    def forecast_prophet(self, model, periods=30):
        """Generate forecast using Prophet."""
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq='D')
        
        # Add holiday regressor for future dates if available
        if 'holiday' in self.df.columns:
            # For simplicity, assume no holidays in future (can be enhanced)
            future['holiday'] = 0
        
        # Make prediction
        forecast = model.predict(future)
        
        # Get only future predictions
        future_forecast = forecast.tail(periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        future_forecast.columns = ['date', 'forecast', 'lower_bound', 'upper_bound']
        
        return future_forecast
    
    def forecast_arima(self, model, periods=30):
        """Generate forecast using ARIMA."""
        # Get forecast
        forecast_result = model.forecast(steps=periods)
        conf_int = model.get_forecast(steps=periods).conf_int()
        
        # Create future dates
        last_date = self.df[self.date_column].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_result.values,
            'lower_bound': conf_int.iloc[:, 0].values,
            'upper_bound': conf_int.iloc[:, 1].values
        })
        
        return forecast_df
    
    def detect_model_type(self, model):
        """Detect if model is Prophet or ARIMA."""
        from prophet import Prophet
        from statsmodels.tsa.arima.model import ARIMAResults
        
        if isinstance(model, Prophet):
            return 'prophet'
        elif isinstance(model, ARIMAResults):
            return 'arima'
        else:
            # Try to detect by checking for Prophet-specific methods
            if hasattr(model, 'make_future_dataframe'):
                return 'prophet'
            else:
                return 'arima'
    
    def generate_forecasts(self, periods=30):
        """
        Generate forecasts for all junctions.
        
        Args:
            periods: Number of days to forecast (default: 30)
        """
        print("\n" + "=" * 50)
        print(f"Generating Forecasts for Next {periods} Days")
        print("=" * 50)
        
        if not self.models:
            print("No models trained. Please run train_models() first.")
            return
        
        for junction, model in self.models.items():
            try:
                # Detect model type
                model_type = self.detect_model_type(model)
                
                if model_type == 'prophet':
                    forecast = self.forecast_prophet(model, periods)
                else:
                    forecast = self.forecast_arima(model, periods)
                
                self.forecasts[junction] = forecast
                print(f"Forecast generated for {junction} using {model_type.upper()}")
                
            except Exception as e:
                print(f"Error forecasting for {junction}: {str(e)}")
                continue
        
        print(f"\nGenerated forecasts for {len(self.forecasts)} junctions")
        return self.forecasts
    
    def get_forecast_summary(self):
        """Get summary of all forecasts."""
        summary = {}
        for junction, forecast in self.forecasts.items():
            summary[junction] = {
                'mean_forecast': forecast['forecast'].mean(),
                'min_forecast': forecast['forecast'].min(),
                'max_forecast': forecast['forecast'].max(),
                'forecast_dates': forecast['date'].tolist(),
                'forecast_values': forecast['forecast'].tolist()
            }
        return summary
    
    def save_forecasts(self, output_dir='forecasts'):
        """Save forecasts to CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        
        for junction, forecast in self.forecasts.items():
            output_path = os.path.join(output_dir, f'{junction}_forecast.csv')
            forecast.to_csv(output_path, index=False)
            print(f"Saved forecast: {output_path}")


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        df = pd.read_csv(data_path)
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        
        forecaster = TrafficForecaster(df, model_type='prophet')
        forecaster.train_models()
        forecaster.generate_forecasts(periods=30)
        forecaster.save_forecasts()
    else:
        print("Usage: python forecasting.py <path_to_processed_data.csv>")


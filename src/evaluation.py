"""
Model Evaluation Module
Calculates MAE, RMSE, and MAPE metrics for forecasting models.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings

warnings.filterwarnings('ignore')


class ModelEvaluator:
    """Evaluate forecasting model performance."""
    
    def __init__(self, df, models, date_column='DateTime', test_size=0.2):
        """
        Initialize evaluator.
        
        Args:
            df: Preprocessed DataFrame
            models: Dictionary of trained models {junction: model}
            date_column: Name of the datetime column
            test_size: Proportion of data to use for testing
        """
        self.df = df.copy().sort_values(by=date_column).reset_index(drop=True)
        self.models = models
        self.date_column = date_column
        self.test_size = test_size
        self.results = {}
    
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
    
    def split_data(self, junction_col):
        """Split data into train and test sets."""
        split_idx = int(len(self.df) * (1 - self.test_size))
        train_df = self.df.iloc[:split_idx].copy()
        test_df = self.df.iloc[split_idx:].copy()
        
        return train_df, test_df
    
    def calculate_mae(self, y_true, y_pred):
        """Calculate Mean Absolute Error."""
        return mean_absolute_error(y_true, y_pred)
    
    def calculate_rmse(self, y_true, y_pred):
        """Calculate Root Mean Squared Error."""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    def calculate_mape(self, y_true, y_pred):
        """Calculate Mean Absolute Percentage Error."""
        # Avoid division by zero
        mask = y_true != 0
        if mask.sum() == 0:
            return np.nan
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    def evaluate_prophet_model(self, model, junction_col):
        """Evaluate Prophet model."""
        from prophet import Prophet
        
        train_df, test_df = self.split_data(junction_col)
        
        # Prepare data
        train_prophet = pd.DataFrame({
            'ds': train_df[self.date_column],
            'y': train_df[junction_col]
        })
        
        # Make predictions on test set
        # Prophet expects a DataFrame with 'ds' column
        future = pd.DataFrame({
            'ds': pd.to_datetime(test_df[self.date_column])
        })
        
        forecast = model.predict(future)
        y_pred = forecast['yhat'].values
        y_true = test_df[junction_col].values
        
        # Calculate metrics
        mae = self.calculate_mae(y_true, y_pred)
        rmse = self.calculate_rmse(y_true, y_pred)
        mape = self.calculate_mape(y_true, y_pred)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'y_true': y_true.tolist(),
            'y_pred': y_pred.tolist()
        }
    
    def evaluate_arima_model(self, model, junction_col):
        """Evaluate ARIMA model."""
        train_df, test_df = self.split_data(junction_col)
        
        # Get predictions
        test_size = len(test_df)
        forecast_result = model.forecast(steps=test_size)
        y_pred = forecast_result.values
        
        y_true = test_df[junction_col].values[:len(y_pred)]
        y_pred = y_pred[:len(y_true)]
        
        # Calculate metrics
        mae = self.calculate_mae(y_true, y_pred)
        rmse = self.calculate_rmse(y_true, y_pred)
        mape = self.calculate_mape(y_true, y_pred)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'y_true': y_true.tolist(),
            'y_pred': y_pred.tolist()
        }
    
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
    
    def evaluate_all_models(self, model_type='prophet'):
        """
        Evaluate all models.
        
        Args:
            model_type: 'prophet' or 'arima' (default, but will auto-detect)
        """
        print("=" * 50)
        print("Evaluating Models")
        print("=" * 50)
        
        for junction, model in self.models.items():
            try:
                # Auto-detect model type
                detected_type = self.detect_model_type(model)
                
                if detected_type == 'prophet':
                    results = self.evaluate_prophet_model(model, junction)
                else:
                    results = self.evaluate_arima_model(model, junction)
                
                self.results[junction] = results
                
                print(f"\n{junction}:")
                print(f"  Model: {detected_type.upper()}")
                print(f"  MAE:  {results['mae']:.2f}")
                print(f"  RMSE: {results['rmse']:.2f}")
                print(f"  MAPE: {results['mape']:.2f}%")
                
            except Exception as e:
                print(f"Error evaluating {junction}: {str(e)}")
                continue
        
        print("\n" + "=" * 50)
        return self.results
    
    def get_summary(self):
        """Get summary of all evaluation results."""
        summary = {
            'junctions': list(self.results.keys()),
            'mae': [self.results[j]['mae'] for j in self.results.keys()],
            'rmse': [self.results[j]['rmse'] for j in self.results.keys()],
            'mape': [self.results[j]['mape'] for j in self.results.keys()],
            'average_mae': np.mean([self.results[j]['mae'] for j in self.results.keys()]),
            'average_rmse': np.mean([self.results[j]['rmse'] for j in self.results.keys()]),
            'average_mape': np.mean([self.results[j]['mape'] for j in self.results.keys()])
        }
        return summary
    
    def save_results(self, output_path='evaluation_results.csv'):
        """Save evaluation results to CSV."""
        results_list = []
        for junction, metrics in self.results.items():
            results_list.append({
                'Junction': junction,
                'MAE': metrics['mae'],
                'RMSE': metrics['rmse'],
                'MAPE': metrics['mape']
            })
        
        results_df = pd.DataFrame(results_list)
        results_df.to_csv(output_path, index=False)
        print(f"\nEvaluation results saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    import sys
    import pickle
    
    if len(sys.argv) > 2:
        data_path = sys.argv[1]
        models_dir = sys.argv[2]
        
        df = pd.read_csv(data_path)
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        
        # Load models
        models = {}
        import os
        for file in os.listdir(models_dir):
            if file.endswith('.pkl'):
                junction = file.replace('_prophet.pkl', '').replace('_arima.pkl', '')
                with open(os.path.join(models_dir, file), 'rb') as f:
                    models[junction] = pickle.load(f)
        
        evaluator = ModelEvaluator(df, models)
        evaluator.evaluate_all_models(model_type='prophet')
        evaluator.save_results()
    else:
        print("Usage: python evaluation.py <data_path> <models_dir>")


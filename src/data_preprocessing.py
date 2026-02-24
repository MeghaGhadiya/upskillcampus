"""
Data Preprocessing Module for Traffic Forecasting
Handles loading, cleaning, and preparing the dataset for modeling.
"""

import pandas as pd
import numpy as np
import holidays
from datetime import datetime
import os


class TrafficDataPreprocessor:
    """Preprocess traffic data for forecasting."""
    
    def __init__(self, data_path=None):
        """
        Initialize the preprocessor.
        
        Args:
            data_path: Path to the CSV file. If None, looks for 'traffic.csv' in current directory.
        """
        self.data_path = data_path or 'traffic.csv'
        self.df = None
        self.processed_df = None
        
    def load_data(self):
        """Load the dataset from CSV file."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}. Please download it first.")
        
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self.df
    
    def handle_missing_values(self):
        """Handle missing values in the dataset."""
        print("\nHandling missing values...")
        initial_missing = self.df.isnull().sum().sum()
        print(f"Initial missing values: {initial_missing}")
        
        # Forward fill for time series data
        self.df = self.df.ffill()
        # Backward fill for any remaining missing values
        self.df = self.df.bfill()
        # If still missing, fill with 0
        self.df = self.df.fillna(0)
        
        final_missing = self.df.isnull().sum().sum()
        print(f"Remaining missing values: {final_missing}")
        
    def remove_duplicates(self):
        """Remove duplicate rows."""
        print("\nRemoving duplicates...")
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        final_count = len(self.df)
        removed = initial_count - final_count
        print(f"Removed {removed} duplicate rows")
        
    def detect_datetime_column(self):
        """Automatically detect datetime column."""
        # Common datetime column names
        datetime_keywords = ['date', 'time', 'datetime', 'timestamp', 'dt']
        
        for col in self.df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in datetime_keywords):
                # Try to convert to see if it's actually datetime
                try:
                    test_series = pd.to_datetime(self.df[col].head(10), errors='coerce')
                    if test_series.notna().sum() > 0:
                        return col
                except:
                    continue
        
        # If no datetime column found, return None
        return None
    
    def convert_to_datetime(self, date_column=None):
        """Convert timestamp column to datetime format."""
        # Auto-detect if not provided
        if date_column is None:
            date_column = self.detect_datetime_column()
            if date_column is None:
                print("Warning: Could not detect datetime column. Available columns:", self.df.columns.tolist())
                return None
        
        print(f"\nConverting {date_column} to datetime...")
        if date_column in self.df.columns:
            self.df[date_column] = pd.to_datetime(self.df[date_column], errors='coerce')
            # Remove rows where datetime conversion failed
            initial_count = len(self.df)
            self.df = self.df.dropna(subset=[date_column])
            removed = initial_count - len(self.df)
            if removed > 0:
                print(f"Removed {removed} rows with invalid datetime")
            # Sort by datetime
            self.df = self.df.sort_values(by=date_column).reset_index(drop=True)
            print("Datetime conversion completed")
            return date_column
        else:
            print(f"Warning: Column '{date_column}' not found. Available columns: {self.df.columns.tolist()}")
            return None
    
    def add_time_features(self, date_column='DateTime'):
        """Add time-based features (hour, day, month, day_of_week)."""
        if date_column not in self.df.columns:
            return
            
        print("\nAdding time features...")
        self.df['hour'] = self.df[date_column].dt.hour
        self.df['day'] = self.df[date_column].dt.day
        self.df['month'] = self.df[date_column].dt.month
        self.df['day_of_week'] = self.df[date_column].dt.dayofweek
        self.df['is_weekend'] = self.df['day_of_week'].isin([5, 6]).astype(int)
        print("Time features added")
    
    def add_holiday_flags(self, date_column='DateTime', country='IN'):
        """
        Add holiday flags to the dataset.
        
        Args:
            date_column: Name of the datetime column
            country: Country code for holidays (default: 'IN' for India)
        """
        if date_column not in self.df.columns:
            return
            
        print(f"\nAdding holiday flags for {country}...")
        
        # Get holidays for the date range in the dataset
        min_date = self.df[date_column].min()
        max_date = self.df[date_column].max()
        
        # Get holidays for India (or specified country)
        if country == 'IN':
            # India holidays
            india_holidays = holidays.India(years=range(min_date.year, max_date.year + 1))
        else:
            india_holidays = holidays.country_holidays(country, years=range(min_date.year, max_date.year + 1))
        
        # Create holiday flag
        # holidays.keys() returns date objects, so we compare directly
        holiday_dates = set(india_holidays.keys())
        self.df['is_holiday'] = self.df[date_column].dt.date.isin(holiday_dates).astype(int)
        
        # Special occasions (you can customize this)
        self.df['is_special_occasion'] = 0
        
        # Mark special occasions (e.g., festivals, events)
        # Example: Diwali period, New Year, etc.
        for idx, row in self.df.iterrows():
            date = row[date_column]
            month = date.month
            day = date.day
            
            # New Year (Jan 1)
            if month == 1 and day == 1:
                self.df.at[idx, 'is_special_occasion'] = 1
            # Republic Day (Jan 26) - India
            if month == 1 and day == 26:
                self.df.at[idx, 'is_special_occasion'] = 1
            # Independence Day (Aug 15) - India
            if month == 8 and day == 15:
                self.df.at[idx, 'is_special_occasion'] = 1
            # Diwali period (October-November, approximate)
            if month == 10 or (month == 11 and day <= 15):
                self.df.at[idx, 'is_special_occasion'] = 1
        
        # Combined flag for holidays or special occasions
        self.df['is_holiday_or_special'] = ((self.df['is_holiday'] == 1) | 
                                           (self.df['is_special_occasion'] == 1)).astype(int)
        
        holiday_count = self.df['is_holiday'].sum()
        special_count = self.df['is_special_occasion'].sum()
        print(f"Added holiday flags: {holiday_count} holidays, {special_count} special occasions")
    
    def reshape_long_to_wide(self, date_column, junction_column='Junction', value_column='Vehicles'):
        """
        Reshape data from long format to wide format if needed.
        Long format: DateTime, Junction, Vehicles
        Wide format: DateTime, Junction_1, Junction_2, Junction_3, Junction_4
        """
        # Check if data is already in wide format (has multiple junction columns)
        junction_cols = [col for col in self.df.columns 
                        if 'junction' in col.lower() and col.lower() != junction_column.lower()]
        
        if junction_cols:
            print("Data is already in wide format. Skipping reshape.")
            return date_column
        
        # Check if we have the long format structure
        if junction_column in self.df.columns and value_column in self.df.columns:
            print(f"\nReshaping data from long to wide format...")
            print(f"  Pivoting: {junction_column} -> columns, {value_column} -> values")
            
            # Pivot the data
            self.df = self.df.pivot_table(
                index=date_column,
                columns=junction_column,
                values=value_column,
                aggfunc='mean'  # In case of duplicates, take mean
            ).reset_index()
            
            # Rename columns to Junction_1, Junction_2, etc.
            new_columns = [date_column]
            for col in self.df.columns[1:]:  # Skip the date column
                new_columns.append(f'Junction_{int(col)}')
            
            self.df.columns = new_columns
            
            print(f"  Reshaped to wide format: {self.df.shape}")
            print(f"  New columns: {self.df.columns.tolist()}")
            
            return date_column
        
        return date_column
    
    def preprocess(self, date_column=None, country='IN'):
        """
        Complete preprocessing pipeline.
        
        Args:
            date_column: Name of the datetime column (None for auto-detect)
            country: Country code for holidays
        """
        print("=" * 50)
        print("Starting Data Preprocessing")
        print("=" * 50)
        
        # Load data
        self.load_data()
        
        # Display initial info
        print(f"\nInitial dataset info:")
        print(f"  Shape: {self.df.shape}")
        print(f"  Columns: {self.df.columns.tolist()}")
        print(f"  First few rows:")
        print(self.df.head())
        
        # Handle missing values
        self.handle_missing_values()
        
        # Remove duplicates
        self.remove_duplicates()
        
        # Convert to datetime (auto-detect if not provided)
        detected_column = self.convert_to_datetime(date_column)
        if detected_column:
            date_column = detected_column
        elif date_column is None:
            # Try common names
            for col_name in ['DateTime', 'Date', 'Time', 'datetime', 'date', 'time']:
                if col_name in self.df.columns:
                    date_column = col_name
                    self.convert_to_datetime(date_column)
                    break
        
        if date_column is None or date_column not in self.df.columns:
            raise ValueError("Could not find or convert datetime column. Please specify date_column parameter.")
        
        # Reshape from long to wide format if needed
        date_column = self.reshape_long_to_wide(date_column)
        
        # Add time features
        self.add_time_features(date_column)
        
        # Add holiday flags
        self.add_holiday_flags(date_column, country)
        
        self.processed_df = self.df.copy()
        
        print("\n" + "=" * 50)
        print("Preprocessing Complete!")
        print("=" * 50)
        print(f"\nDataset shape: {self.processed_df.shape}")
        print(f"\nColumns: {self.processed_df.columns.tolist()}")
        if date_column in self.processed_df.columns:
            print(f"\nDate range: {self.processed_df[date_column].min()} to {self.processed_df[date_column].max()}")
        
        return self.processed_df
    
    def save_processed_data(self, output_path='traffic_processed.csv'):
        """Save the processed dataset."""
        if self.processed_df is not None:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            self.processed_df.to_csv(output_path, index=False)
            print(f"\nProcessed data saved to {output_path}")
        else:
            print("No processed data available. Run preprocess() first.")


if __name__ == "__main__":
    # Example usage
    preprocessor = TrafficDataPreprocessor()
    try:
        df = preprocessor.preprocess()
        preprocessor.save_processed_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please download the dataset first and place it as 'traffic.csv' in the project directory.")


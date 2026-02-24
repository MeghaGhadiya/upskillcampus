"""
Exploratory Data Analysis Module
Creates visualizations for traffic patterns, holidays, peak hours, and seasonal trends.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime


class TrafficEDA:
    """Perform exploratory data analysis on traffic data."""
    
    def __init__(self, df, date_column='DateTime'):
        """
        Initialize EDA.
        
        Args:
            df: Preprocessed DataFrame
            date_column: Name of the datetime column
        """
        self.df = df.copy()
        self.date_column = date_column
        # Use project root for plots directory
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / 'plots'
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def get_junction_columns(self):
        """Get column names for traffic junctions."""
        # Look for columns that might represent junctions
        junction_cols = [col for col in self.df.columns 
                        if 'junction' in col.lower() or 'traffic' in col.lower() 
                        or col.isdigit() or 'Junction' in col]
        
        # If no specific junction columns found, look for numeric columns (excluding time features)
        if not junction_cols:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = ['hour', 'day', 'month', 'day_of_week', 'is_weekend', 
                          'is_holiday', 'is_special_occasion', 'is_holiday_or_special']
            junction_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        return junction_cols[:4] if len(junction_cols) >= 4 else junction_cols
    
    def plot_traffic_trends(self):
        """Visualize traffic trends for each junction over time."""
        print("\nCreating traffic trends plots...")
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            print("No junction columns found!")
            return
        
        fig, axes = plt.subplots(len(junction_cols), 1, figsize=(15, 4 * len(junction_cols)))
        if len(junction_cols) == 1:
            axes = [axes]
        
        for idx, junction in enumerate(junction_cols):
            ax = axes[idx]
            self.df.plot(x=self.date_column, y=junction, ax=ax, linewidth=0.5, alpha=0.7)
            ax.set_title(f'Traffic Trends - {junction}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Traffic Count', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend([junction])
        
        plt.tight_layout()
        plt.savefig(str(self.output_dir / 'traffic_trends.png'), dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir / 'traffic_trends.png'}")
        plt.close()
    
    def plot_working_days_vs_holidays(self):
        """Compare traffic patterns on normal working days vs holidays."""
        print("\nCreating working days vs holidays comparison...")
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            return
        
        if 'is_holiday_or_special' not in self.df.columns:
            print("Holiday flags not found in dataset!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, junction in enumerate(junction_cols[:4]):
            ax = axes[idx]
            
            # Group by holiday status
            normal_days = self.df[self.df['is_holiday_or_special'] == 0][junction]
            holiday_days = self.df[self.df['is_holiday_or_special'] == 1][junction]
            
            # Create comparison plot
            data_to_plot = [normal_days.values, holiday_days.values]
            bp = ax.boxplot(data_to_plot, labels=['Normal Days', 'Holidays/Special'], 
                          patch_artist=True)
            
            # Color the boxes
            colors = ['lightblue', 'lightcoral']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_title(f'{junction}: Normal Days vs Holidays', fontsize=12, fontweight='bold')
            ax.set_ylabel('Traffic Count', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(str(self.output_dir / 'working_days_vs_holidays.png'), dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir / 'working_days_vs_holidays.png'}")
        plt.close()
    
    def plot_peak_hours(self):
        """Identify and visualize peak hours for each junction."""
        print("\nCreating peak hours analysis...")
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            return
        
        if 'hour' not in self.df.columns:
            print("Hour feature not found!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, junction in enumerate(junction_cols[:4]):
            ax = axes[idx]
            
            # Calculate average traffic by hour
            hourly_avg = self.df.groupby('hour')[junction].mean()
            
            # Plot
            ax.bar(hourly_avg.index, hourly_avg.values, color='steelblue', alpha=0.7)
            ax.set_title(f'{junction}: Average Traffic by Hour', fontsize=12, fontweight='bold')
            ax.set_xlabel('Hour of Day', fontsize=11)
            ax.set_ylabel('Average Traffic Count', fontsize=11)
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3, axis='y')
            
            # Highlight peak hours
            peak_hours = hourly_avg.nlargest(3).index
            for peak in peak_hours:
                ax.axvline(x=peak, color='red', linestyle='--', alpha=0.5, linewidth=2)
        
        plt.tight_layout()
        plt.savefig(str(self.output_dir / 'peak_hours.png'), dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir / 'peak_hours.png'}")
        plt.close()
    
    def plot_seasonal_patterns(self):
        """Visualize seasonal patterns in traffic."""
        print("\nCreating seasonal patterns analysis...")
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            return
        
        if 'month' not in self.df.columns:
            print("Month feature not found!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, junction in enumerate(junction_cols[:4]):
            ax = axes[idx]
            
            # Calculate average traffic by month
            monthly_avg = self.df.groupby('month')[junction].mean()
            
            # Plot
            ax.plot(monthly_avg.index, monthly_avg.values, marker='o', 
                   linewidth=2, markersize=8, color='darkgreen')
            ax.fill_between(monthly_avg.index, monthly_avg.values, alpha=0.3, color='lightgreen')
            ax.set_title(f'{junction}: Seasonal Traffic Patterns', fontsize=12, fontweight='bold')
            ax.set_xlabel('Month', fontsize=11)
            ax.set_ylabel('Average Traffic Count', fontsize=11)
            ax.set_xticks(range(1, 13))
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(str(self.output_dir / 'seasonal_patterns.png'), dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir / 'seasonal_patterns.png'}")
        plt.close()
    
    def plot_weekday_patterns(self):
        """Visualize traffic patterns by day of week."""
        print("\nCreating weekday patterns analysis...")
        junction_cols = self.get_junction_columns()
        
        if not junction_cols:
            return
        
        if 'day_of_week' not in self.df.columns:
            print("Day of week feature not found!")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for idx, junction in enumerate(junction_cols[:4]):
            ax = axes[idx]
            
            # Calculate average traffic by day of week
            daily_avg = self.df.groupby('day_of_week')[junction].mean()
            
            # Plot
            ax.bar(range(7), daily_avg.values, color='coral', alpha=0.7)
            ax.set_title(f'{junction}: Traffic by Day of Week', fontsize=12, fontweight='bold')
            ax.set_xlabel('Day of Week', fontsize=11)
            ax.set_ylabel('Average Traffic Count', fontsize=11)
            ax.set_xticks(range(7))
            ax.set_xticklabels(weekdays)
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(str(self.output_dir / 'weekday_patterns.png'), dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir / 'weekday_patterns.png'}")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all EDA visualizations."""
        print("=" * 50)
        print("Generating EDA Visualizations")
        print("=" * 50)
        
        self.plot_traffic_trends()
        self.plot_working_days_vs_holidays()
        self.plot_peak_hours()
        self.plot_seasonal_patterns()
        self.plot_weekday_patterns()
        
        print("\n" + "=" * 50)
        print("EDA Complete! All plots saved to 'plots' directory")
        print("=" * 50)


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        df = pd.read_csv(data_path)
        eda = TrafficEDA(df)
        eda.generate_all_plots()
    else:
        print("Usage: python eda.py <path_to_processed_data.csv>")


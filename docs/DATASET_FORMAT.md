# Dataset Format Guide

## Expected Dataset Structure

The traffic forecasting system expects a CSV file with the following structure:

### Required Columns

1. **DateTime** (or similar datetime column)
   - Format: Should be parseable as datetime (e.g., "YYYY-MM-DD HH:MM:SS", "MM/DD/YYYY HH:MM", etc.)
   - Contains: Timestamp for each traffic reading

2. **Traffic Count Columns** (for each junction)
   - The system automatically detects junction columns
   - Common names: "Junction 1", "Junction 2", "Junction 3", "Junction 4"
   - Or: "Traffic_Junction_1", "Traffic_Junction_2", etc.
   - Or: Numeric column names like "1", "2", "3", "4"
   - Contains: Traffic count/volume for each junction at each timestamp

### Example Dataset Structure

```csv
DateTime,Junction 1,Junction 2,Junction 3,Junction 4
2015-11-01 00:00:00,15,12,18,20
2015-11-01 01:00:00,10,8,12,15
2015-11-01 02:00:00,8,6,10,12
...
```

### Alternative Formats

The system is flexible and can handle:

- Different datetime formats
- Different junction naming conventions
- Missing values (will be handled automatically)
- Duplicate rows (will be removed)

### Minimum Requirements

- At least one datetime column
- At least one numeric column representing traffic counts
- Data should be time-ordered (will be sorted automatically)

### Data Preprocessing Applied

The system automatically:
1. Converts timestamps to datetime format
2. Handles missing values (forward fill, backward fill, then zero fill)
3. Removes duplicate rows
4. Adds time features (hour, day, month, day of week)
5. Detects weekends
6. Flags holidays (using India holidays by default)
7. Flags special occasions

### Notes

- The system works best with hourly or daily data
- More data points generally lead to better forecasts
- At least 1-2 months of historical data is recommended for good forecasts
- The system can handle up to 4 junctions (will use the first 4 detected)


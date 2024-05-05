import pandas as pd
from datetime import datetime, timedelta
from cryptoindex import fetch_crypto_data
from cryptoindex import update_weights       # Assuming cryptoindex is in the same directory as updater.py
from cryptoindex import get_crypto_index


def update_weights(crypto_data):
    _, dfs = get_crypto_index(crypto_data)
    
    # Check if dfs is empty
    if dfs.empty:
        print("No valid DataFrames to calculate weights.")
        return None  # or return an empty DataFrame if needed
    
    # Get the row with the latest date if 'date' column exists
    if 'date' in dfs.columns:
        latest_date_row = dfs[dfs['date'] == dfs['date'].max()]
        
        # Check if the latest_date_row is empty
        if latest_date_row.empty:
            print("No data available for the latest date.")
            return None  # or handle this case as needed
        
        return latest_date_row
    else:
        print("No 'date' column found in the DataFrame.")
        return None  # or handle this case as needed



def calc_dates(date: datetime = datetime.now()) -> tuple:
    """
    Calculate start and end dates for a given date.
    """
    this_year = date - timedelta(days=date.day-1)
    one_year = this_year + timedelta(days=-365)
    return (one_year.strftime("%Y-%m-%d"), this_year.strftime("%Y-%m-%d"))

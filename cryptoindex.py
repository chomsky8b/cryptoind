import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_grouped_daily_aggs(date, locale='global', market_type='crypto'):
    """
    Get daily aggregates for a specific date.
    """
    # Mock data for testing
    return pd.DataFrame()

def calc_dates(date: datetime = datetime.now()) -> tuple:
    """
    Calculate start and end dates for a given date.
    """
    this_year = date - timedelta(days=date.day-1)
    one_year = this_year + timedelta(days=-365)
    return (one_year.strftime("%Y-%m-%d"), this_year.strftime("%Y-%m-%d"))

def get_daily_bars(ticker:str, date=datetime.now()):
    """
    Get daily bars for a specific ticker and date.
    """
    # Mock data for testing
    return pd.DataFrame()

def update_day(last_day, func=np.sqrt):
    """
    Update the DataFrame for a given day using a specified function.
    """
    dflist = []
    for ticker in last_day.ticker:
        dflist.append(get_daily_bars(ticker))
    newdf = pd.concat(dflist, axis=1)
    oldind = newdf.index
    last_day_r = last_day.reset_index(drop=True)
    newdf_r = newdf.reset_index(drop=True)
    close_column = last_day['close']
    newdf_r.index = oldind
    newdf_r["indprice"] = newdf_r.apply(lambda x: np.average(x, weights=func(last_day.weight)), axis=1)
    return newdf_r.indprice.ffill()

def get_crypto_index(crypto_data, howmany=2, func=lambda x: x):
    ser = pd.Series(np.ones(howmany)).map(func)
    p = pd.Series(np.ones(howmany))
    valdict = {}
    dfdict = {}
    vallist = []  # Initialize an empty list to store DataFrames
    
    # Iterate over each ticker group in the crypto_data DataFrame
    for ticker, df in crypto_data.groupby('ticker'):
        # Check DataFrame column names
        print(f"Columns for ticker {ticker}:", df.columns)
        
        # Check if 'open' column is present in the DataFrame
        if 'open' in df.columns:
            # Calculate 'totalvol_ema' if it's not already present
            if 'totalvol_ema' not in df.columns:
                df['totalvol_ema'] = df['volume'] * df['open']  # Example calculation, replace with actual calculation
            
            # Filter DataFrame by 'open' values greater than 0.01
            df_filtered = df[df['open'] > 0.01]
            
            # Check if any rows are filtered out
            if df_filtered.empty:
                print(f"No rows with 'open' > 0.01 for ticker {ticker}. Skipping.")
                continue
            
            # Sort DataFrame by 'totalvol_ema' in descending order and select top howmany rows
            df_sorted = df_filtered.sort_values('totalvol_ema', ascending=False).head(howmany)
            
            # Check if any rows are selected after sorting
            if df_sorted.empty:
                print(f"No valid rows after sorting for ticker {ticker}. Skipping.")
                continue
            
            # Calculate aggregated values
            indopen = np.average(df_sorted['open'].values, weights=ser.values)
            indclose = np.average(df_sorted['close'].values, weights=ser.values)
            
            # Map 'totalvol_ema' through the given function
            ser = df_sorted['totalvol_ema'].map(func)
            p = df_sorted['close']
            
            # Store aggregated values in valdict
            valdict[ticker] = {'open': indopen, 'close': indclose}
            
            # Create DataFrame with ticker, weight, and close columns
            dfdict[ticker] = pd.DataFrame({'ticker': df_sorted['ticker'], 'weight': ser, 'close': df_sorted['close']})
            
            # Append the DataFrame to vallist for concatenation
            vallist.append(dfdict[ticker])
        else:
            # Skip if 'open' column is not found
            print(f"No 'open' column found for ticker {ticker}. Skipping.")
    
    # Create DataFrame from valdict
    vals = pd.DataFrame(valdict).T
    
    # Concatenate DataFrames in vallist if it's not empty
    if vallist:
        dfs = pd.concat(vallist)
    else:
        print("No valid DataFrames to concatenate. Returning empty DataFrame.")
        dfs = pd.DataFrame()
    
    return vals, dfs





def update_weights(crypto_data, **kwargs):
    """
    Update weights based on the provided cryptocurrency data.
    """
    _, dfs = get_crypto_index(crypto_data)
    if dfs is not None:
        retval = dfs[dfs.date == dfs.date.max()]
        retval.to_csv("/tmp/wts.csv", index=False)
        return retval
    else:
        print("No DataFrame found. Unable to update weights.")
        return None

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calc_dates(date: datetime = datetime.now()) -> tuple:
    this_year = date - timedelta(days=date.day-1)
    one_year = this_year + timedelta(days=-365)
    return (one_year.strftime("%Y-%m-%d"), this_year.strftime("%Y-%m-%d"))

def get_crypto_index(crypto_data, howmany=2, func=lambda x: x):
    ser = pd.Series(np.ones(howmany)).map(func)
    p = pd.Series(np.ones(howmany))
    valdict = {}
    dfdict = {}
    vallist = []  # Initialize an empty list to store DataFrames
    for ticker, df in crypto_data.groupby('ticker'):
        # Check DataFrame column names
        print(f"Columns for ticker {ticker}:", df.columns)
        
        # Adjust condition to check for 'open' column or another relevant column
        if 'open' in df.columns:
            df = df[df['open'] > 0.01]
            df = df.sort_values('totalvol_ema', ascending=False).head(howmany)
            indopen = np.average(df['open'].values, weights=ser.values)
            indclose = np.average(df['close'].values, weights=ser.values)
            ser = df['totalvol_ema'].map(func)
            p = df['close']
            valdict[ticker] = {'open': indopen, 'close': indclose}
            dfdict[ticker] = pd.DataFrame({'ticker': df['ticker'], 'weight': ser, 'close': df['close']})
            # Append the DataFrame to vallist
            vallist.append(dfdict[ticker])
        else:
            print(f"No 'open' column found for ticker {ticker}. Skipping.")

    vals = pd.DataFrame(valdict).T
    
    # Concatenate DataFrames only if vallist is not empty
    if vallist:
        dfs = pd.concat(vallist)
    else:
        print("No valid DataFrames to concatenate. Returning empty DataFrame.")
        dfs = pd.DataFrame()
    
    return vals, dfs




import pandas as pd
from datetime import datetime


import pandas as pd

def fetch_crypto_data(start_date, end_date, *, locale='global', market_type='crypto', from_csv=True):
    """
    Fetch cryptocurrency data from an external source.

    Parameters:
    - start_date (str): Start date in YYYY-MM-DD format.
    - end_date (str): End date in YYYY-MM-DD format.
    - locale (str): Locale for data (default is 'global').
    - market_type (str): Market type for data (default is 'crypto').
    - from_csv (bool): Flag to indicate whether to fetch data from CSV file (default is True).

    Returns:
    - pd.DataFrame: DataFrame containing cryptocurrency data.
    """
    if from_csv:
        # Assuming data is stored in a CSV file named 'crypto_data.csv'
        try:
            data = pd.read_csv('crypto_data.csv')
            # Filter data based on start_date and end_date
            data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
            return data
        except FileNotFoundError:
            print("CSV file 'crypto_data.csv' not found.")
            return pd.DataFrame()  # Return empty DataFrame if file not found
    else:
        # Implement fetching data from other sources (e.g., APIs, databases, web scraping)
        pass  # Placeholder for other implementations



    return pd.DataFrame()


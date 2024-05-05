import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_crypto_data(num_days=1000, num_coins=30):
    """
    Generate test cryptocurrency data with daily values for all required attributes for all coins.

    Parameters:
    - num_days (int): Number of days of data to generate (default is 365).
    - num_coins (int): Number of coins to generate (default is 30).

    Returns:
    - pd.DataFrame: DataFrame containing test cryptocurrency data.
    """
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days-1)
    date_range = pd.date_range(start=start_date, end=end_date)

    # Generate ticker symbols
    tickers = ['BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'ADAUSD', 'BNBUSD', 'DOGEUSD', 'LINKUSD', 'XLMUSD', 'TRXUSD',
               'EOSUSD', 'BCHUSD', 'ETCUSD', 'VETUSD', 'DASHUSD', 'NEOUSD', 'XTZUSD', 'ATOMUSD', 'MKRUSD', 'ONTUSD',
               'LEOUSD', 'ICXUSD', 'BATUSD', 'ZECUSD', 'WAVESUSD', 'ZRXUSD', 'ALGOUSD', 'COMPUSD', 'OMGUSD', 'KNCUSD']

    # Generate random values for each attribute
    open_prices = np.random.uniform(low=1, high=10000, size=(num_days, num_coins))
    volumes = np.random.uniform(low=100, high=1000000, size=(num_days, num_coins))
    market_caps = np.random.uniform(low=1000000, high=1000000000, size=(num_days, num_coins))

    # Flatten arrays
    open_prices_flat = open_prices.flatten()
    volumes_flat = volumes.flatten()
    market_caps_flat = market_caps.flatten()

    # Repeat dates and tickers to match the length of the flattened arrays
    dates = np.repeat(date_range, num_coins)
    tickers = np.tile(tickers, num_days)

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'ticker': tickers,
        'open': open_prices_flat,
        'volume': volumes_flat,
        'marketcap': market_caps_flat
    })

    return df

if __name__ == "__main__":
    crypto_data = generate_crypto_data()
    crypto_data.to_csv('crypto_data.csv', index=False)
    print("Test cryptocurrency data generated and saved to 'crypto_data.csv'.")

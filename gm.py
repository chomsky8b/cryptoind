import requests
import numpy as np
import pandas as pd
from scipy.stats import binned_statistic

# Polygon API parameters
api_key = 'ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE'
symbol = 'SPY'  # Changed from 'AAPL' to 'SPY'
date = '2024-05-01'

# Get intraday data from Polygon
response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{date}/{date}?apiKey={api_key}')
data = response.json()

# Check if the API request was successful
if response.status_code == 200:
    # Check if 'results' key exists in the data
    if 'results' in data:
        # Convert to DataFrame
        df = pd.DataFrame(data['results'])
        df['t'] = pd.to_datetime(df['t'], unit='ms')
        df.set_index('t', inplace=True)

        # Calculate volume profile
        bins = np.arange(df['l'].min(), df['h'].max(), 1)  # change the bin size as needed
        hist, bin_edges = np.histogram(df['c'], bins=bins, weights=df['v'])
        volume_profile = pd.DataFrame({'price': bin_edges[:-1], 'volume': hist})

        # Find the price level with the largest volume
        largest_volume_price = volume_profile.loc[volume_profile['volume'].idxmax(), 'price']

        print(volume_profile)
        print('Price level with the largest volume:', largest_volume_price)
    else:
        print('Key "results" does not exist in the data.')
else:
    print('API request failed with status code:', response.status_code)

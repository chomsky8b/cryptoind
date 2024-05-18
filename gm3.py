import requests
import numpy as np
import pandas as pd
from scipy.stats import binned_statistic
import backtrader as bt
import datetime

# Polygon API parameters
api_key = 'ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE'
symbol = 'SPY'
date = '2024-02-01'

# Get intraday data from Polygon
minute_response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}?apiKey={api_key}')
minute_data = minute_response.json()

hour_response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/hour/{date}/{date}?apiKey={api_key}')
hour_data = hour_response.json()

# Convert to DataFrames
minute_df = pd.DataFrame(minute_data['results'])
minute_df['t'] = pd.to_datetime(minute_df['t'], unit='ms')
minute_df.set_index('t', inplace=True)

hour_df = pd.DataFrame(hour_data['results'])
hour_df['t'] = pd.to_datetime(hour_df['t'], unit='ms')
hour_df.set_index('t', inplace=True)

# Calculate volume profiles
minute_bins = np.arange(minute_df['l'].min(), minute_df['h'].max(), 0.01)  # change the bin size as needed
minute_hist, minute_bin_edges = np.histogram(minute_df['c'], bins=minute_bins, weights=minute_df['v'])
minute_volume_profile = pd.DataFrame({'price': minute_bin_edges[:-1], 'volume': minute_hist})

hour_bins = np.arange(hour_df['l'].min(), hour_df['h'].max(), 0.1)  # change the bin size as needed
hour_hist, hour_bin_edges = np.histogram(hour_df['c'], bins=hour_bins, weights=hour_df['v'])
hour_volume_profile = pd.DataFrame({'price': hour_bin_edges[:-1], 'volume': hour_hist})

# Find the price levels with the largest volume
minute_poc = minute_volume_profile.loc[minute_volume_profile['volume'].idxmax(), 'price']
hour_poc = hour_volume_profile.loc[hour_volume_profile['volume'].idxmax(), 'price']

print(f"Minute POC level: {minute_poc}")
print(f"Hour POC level: {hour_poc}")

class VolumeProfileStrategy(bt.Strategy):
    params = (('minute_poc', minute_poc), ('hour_poc', hour_poc))

    def __init__(self):
        self.order = None  # To keep track of pending orders

    def next(self):
        # Check if an order is pending, if yes, we cannot send a second one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the price crosses above both the minute and hour POC levels, buy
            if self.data.close[0] > self.params.minute_poc and self.data.close[0] > self.params.hour_poc:
                print(f"Buy Signal: Price {self.data.close[0]} > Minute POC {self.params.minute_poc} and Hour POC {self.params.hour_poc}")
                self.order = self.buy()

        else:
            # We are already in the market, look for a signal to CLOSE trades

            # If the price crosses below either the minute or hour POC level, sell
            if self.data.close[0] < self.params.minute_poc or self.data.close[0] < self.params.hour_poc:
                print(f"Sell Signal: Price {self.data.close[0]} < Minute POC {self.params.minute_poc} or Hour POC {self.params.hour_poc}")
                self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED, Price: {order.executed.price}')
            elif order.issell():
                print(f'SELL EXECUTED, Price: {order.executed.price}')

        # Write down that there's no order
        self.order = None

# Create a cerebro instance
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(VolumeProfileStrategy)

# Create a data feed
data = bt.feeds.PandasData(dataname=minute_df)

# Add the data feed to cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

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
response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{date}/{date}?apiKey={api_key}')
data = response.json()

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

class VolumeProfileStrategy(bt.Strategy):
    params = (('volume_price', largest_volume_price),)

    def __init__(self):
        self.order = None  # To keep track of pending orders

    def next(self):
        # Check if an order is pending, if yes, we cannot send a second one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the price crosses above the volume_price level, buy
            if self.data.close[0] > self.params.volume_price:
                self.order = self.buy()

        else:
            # We are already in the market, look for a signal to CLOSE trades

            # If the price crosses below the volume_price level, sell
            if self.data.close[0] < self.params.volume_price:
                self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                print('BUY EXECUTED,', order.executed.price)
            elif order.issell():
                print('SELL EXECUTED,', order.executed.price)

        # Write down that there's no order
        self.order = None

# Create a cerebro instance
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(VolumeProfileStrategy)

# Create a data feed
data = bt.feeds.PandasData(dataname=df)

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

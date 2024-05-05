import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
date_format = '%Y-%m-%d'
df = pd.read_csv("crypto_data_20_years_original.csv", parse_dates=[0], date_format=date_format, header=None, skiprows=1)

# Rename columns
df.columns = ["Date", "Currency", "Price", "Volume", "MarketCap"]

# Remove specific tickers
tickers_to_remove = ['USDT', 'USDC']
df = df[~df['Currency'].isin(tickers_to_remove)]

# Drop duplicate rows
df = df.drop_duplicates(subset=['Date', 'Currency'], keep='first')

# Define a function to convert currency values
def convert_currency(x):
    x = x.replace('\u202f', '').replace(',', '')
    try:
        if x.endswith('B'):
            return float(x.replace('B', '')) * 1e9
        elif x.endswith('T'):
            return float(x.replace('T', '')) * 1e12
        elif x.endswith('M'):
            return float(x.replace('M', '')) * 1e6
        else:
            return float(x)
    except:
        return np.nan

# Apply currency conversion to relevant columns
df['Volume'] = df['Volume'].apply(convert_currency)
df['MarketCap'] = df['MarketCap'].apply(convert_currency)
df['Price'] = df['Price'].apply(convert_currency)

print(df)

# Group by date and calculate weights
indict = {}
weightdict = []
for i, j in df.groupby('Date'):
    j = j.nlargest(20,"Volume").reset_index(drop=True)
    w = np.sqrt(j['MarketCap'])
    weightdf = pd.DataFrame(w/j["Price"]/100000)
    weightdf["Date"] = i
    weightdf["Currency"] = j["Currency"]
    weightdf["TotalCap"] = w/1000
    weightdf['Price'] = j['Price']
    weightdf.columns = ["Weight", "Date", "Currency", "TotalCap", "Price"]
    weightdict.append(weightdf)
    indict[i] = np.sum(w)

# Create a Series from the dictionary 'indict'
indser = pd.Series(indict)
indser.name = "Index"

print(indser)

# Concatenate the list of DataFrames into a single DataFrame
weightdf = pd.concat(weightdict, ignore_index=True)

# Plot the total market capitalization index
indser.plot()

# Show the plot
plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from tqdm import tqdm  # instead of from tqdm.notebook import tqdm

import requests
from bs4 import BeautifulSoup
import csv

def scrape_and_store_data(numdays = 365):
    # Get today's date
    today = dt.datetime.now()  # Use dt.datetime.now() instead of datetime.now()

    # Open CSV file in append mode
    with open('crypto_data_year.csv', 'a', newline='') as file:
        writer = csv.writer(file)

        # Iterate over 365 days
        for i in tqdm(range(numdays)):  # modified here
            # Calculate the date for the URL
            date_str = (today - dt.timedelta(days=i)).strftime('%Y-%m-%d')
            url = f"https://coincodex.com/historical-data/crypto/?date={date_str}"

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all rows of the table containing cryptocurrency data
                rows = soup.find_all('tr', class_='coin')

                # Iterate over each row and extract relevant data
                for row in rows:
                    # Extract data from the row
                    ticker_elem = row.find(class_='ticker')
                    open_elem = row.find(class_='price')
                    volume_elem = row.find(class_='volume')
                    market_cap_elem = row.find(class_='market-cap')

                    # Check if all elements are found
                    if ticker_elem and open_elem and volume_elem and market_cap_elem:
                        ticker = ticker_elem.text.strip()
                        open_price = open_elem.text.strip().replace('$', '').replace(',', '')
                        volume = volume_elem.text.strip().replace('$', '').replace(',', '')
                        market_cap = market_cap_elem.text.strip().replace('$', '').replace(',', '')

                        # Write the data to the CSV file
                        writer.writerow([date_str, ticker, open_price, volume, market_cap])
                    else:
                        print("Failed to extract data from a row.")
                print(f"Data for {date_str} has been scraped and stored successfully!")
            else:
                print(f"Failed to retrieve data for {date_str} from the website.")

#scrape_and_store_data(2000)

df = pd.read_csv("crypto_data_year.csv", parse_dates = [0], header=None)
df.columns = ["Date","Currency", "Price", "Volume", "MarketCap"]

def convert_currency(x):
    # Remove any non-standard white-space and possible 'M' (millions) if present
    x = x.replace('\u202f', '').replace(',', '')
    try:
      if x.endswith('B'):
        return float(x.replace('B', '')) * 1e9
      elif x.endswith('T'):
        return float(x.replace('T', '')) * 1e12
      elif x.endswith('M'):  # Assuming you might have 'M' for millions as well
        return float(x.replace('M', '')) * 1e6
      else:
        return float(x)
    except:
      return np.nan

# Apply the conversion
df['Volume'] = df['Volume'].apply(convert_currency)
df['MarketCap'] = df['MarketCap'].apply(convert_currency)
df['Price'] = df['Price'].apply(convert_currency)

# Define the tickers to remove
tickers_to_remove = ['USDT', 'USDC']

df = df[~df['Currency'].isin(tickers_to_remove)]
df.sort_values(by = "Date", inplace=True)

df = df.drop_duplicates(subset=['Date', 'Currency'], keep='first')

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

indser = pd.Series(indict)
indser.name = "Index"
weightdf = pd.concat(weightdict, ignore_index=True)

indser.plot()

# After creating the plot
plt.savefig('plot1.png')


weightdf[weightdf["Date"]=='2024-01-01']

btcw = weightdf[weightdf["Currency"] == "BTC"]
btcw.set_index("Date", inplace=True)

btcw.Weight.plot()


# After creating the plot
plt.savefig('plot2.png')

indser.describe()

indser.pct_change().describe()

df[df.Currency == "BTC"].Price.pct_change().describe()

weight_pivot = weightdf.pivot(index='Date', columns='Currency', values='Weight').fillna(value= 0)

weight_pivot.head()

weight_pivot_d = weight_pivot.diff()

price_pivot = weightdf.pivot(index='Date', columns='Currency', values='Price').fillna(value= 0)

volpivot = weight_pivot_d * price_pivot

volpivot.head()

totaltrans = np.abs(volpivot).sum(axis=1)

totaltrans.head()

indser.head()

ind_trans = pd.concat([indser, totaltrans], axis=1)

ind_trans.columns = ["Index", "TotalTrans"]

ind_trans.head()

ind_trans["Frac"] = (ind_trans["TotalTrans"]/ind_trans["Index"]).dropna()

ind_trans.describe()

ind_trans["FracAnnualized"] = ind_trans["Frac"] * 365

ind_trans.describe()

ind_trans.Frac.plot()

volpivot.info()

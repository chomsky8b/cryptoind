import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import csv  
from datetime import datetime, timedelta

def scrape_and_store_data(numdays=365):
    # Get today's date
    today = datetime.now()

    # Open CSV file in append mode
    with open('crypto_data_igor_test.csv', 'a', newline='') as file:
        writer = csv.writer(file)

        # Iterate over 365 days
        for i in range(numdays):
            # Calculate the date for the URL
            date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
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
                        pass#print("Failed to extract data from a row.")

                pass#print(f"Data for {date_str} has been scraped and stored successfully!")
            else:
                print(f"Failed to retrieve data for {date_str} from the website.")

scrape_and_store_data(10)

# Load data from CSV file
df = pd.read_csv("crypto_data_igor_test.csv", parse_dates=[0], header=None)
df.columns = ["Date", "Currency", "Price", "Volume", "MarketCap"]

# Define the function to convert currency
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

# Apply currency conversion
df['Volume'] = df['Volume'].apply(convert_currency)
df['MarketCap'] = df['MarketCap'].apply(convert_currency)
df['Price'] = df['Price'].apply(convert_currency)

# Define the tickers to remove
tickers_to_remove = ['USDT', 'USDC']
df = df[~df['Currency'].isin(tickers_to_remove)]

df.sort_values(by="Date", inplace=True)
df = df.drop_duplicates(subset=['Date', 'Currency'], keep='first')

# Calculate weights and index
indict = {}
weightdict = []
for date, group in df.groupby('Date'):
    top_20 = group.nlargest(20, "Volume").reset_index(drop=True)
    w = np.sqrt(top_20['MarketCap'])
    weightdf = pd.DataFrame(w / top_20["Price"] / 1000)
    weightdf["Date"] = date
    weightdf["Currency"] = top_20["Currency"]
    weightdf["TotalCap"] = w / 1000
    weightdf.columns = ["Weight", "Date", "Currency", "TotalCap"]
    weightdict.append(weightdf)
    indict[date] = np.sum(w)

indser = pd.Series(indict)
indser.name = "Index"
weightdf = pd.concat(weightdict, ignore_index=True)

# Plot the index
indser.plot()

# # Plot the weight of Bitcoin (BTC)
# btcw = weightdf[weightdf["Currency"] == "BTC"]
# btcw.set_index("Date", inplace=True)
# btcw.Weight.plot()

# # Display descriptive statistics
# print(indser.describe())
# print(indser.pct_change().describe())
# print(df[df.Currency == "BTC"].Price.pct_change().describe())

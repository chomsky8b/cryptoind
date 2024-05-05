import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import re

def scrape_and_store_data():
    # Define start and end dates
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()

    # Open CSV file in append mode
    with open('crypto_data_temp.csv', 'a', newline='') as file:
        writer = csv.writer(file)

        # Iterate over the date range
        current_date = end_date
        while current_date >= start_date:
            # Check if data for current date already exists in the CSV
            if not is_data_in_csv(current_date):
                # Fetch data from the website
                fetch_and_store_data(current_date, writer)
            else:
                print(f"Data for {current_date.strftime('%Y-%m-%d')} already exists in CSV.")
            # Move to the previous day
            current_date -= timedelta(days=1)

def is_data_in_csv(date):
    # Check if data for the given date exists in the CSV
    with open('crypto_data_temp.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == date.strftime('%Y-%m-%d'):
                return True
    return False

def fetch_and_store_data(date, writer):
    # Create URL for the given date
    date_str = date.strftime('%Y-%m-%d')
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
                
                # Convert open price to float
                open_price_str = re.sub(r'[^\d.]+', '', open_elem.text.strip())
                open_price = float(open_price_str)
                
                # Convert volume to float
                volume_str = volume_elem.text.strip().replace('$', '').replace(',', '').replace('\u202f', '')
                if 'K' in volume_str:
                    volume = float(volume_str.replace('K', '')) * 1e3
                elif 'M' in volume_str:
                    volume = float(volume_str.replace('M', '')) * 1e6
                elif 'B' in volume_str:
                    volume = float(volume_str.replace('B', '')) * 1e9
                elif 'T' in volume_str:
                    volume = float(volume_str.replace('T', '')) * 1e12
                else:
                    volume = float(volume_str)
                
                # Convert market cap to float
                market_cap_str = market_cap_elem.text.strip().replace('$', '').replace(',', '').replace('\u202f', '')
                if 'K' in market_cap_str:
                    market_cap = float(market_cap_str.replace('K', '')) * 1e3
                elif 'M' in market_cap_str:
                    market_cap = float(market_cap_str.replace('M', '')) * 1e6
                elif 'B' in market_cap_str:
                    market_cap = float(market_cap_str.replace('B', '')) * 1e9
                elif 'T' in market_cap_str:
                    market_cap = float(market_cap_str.replace('T', '')) * 1e12
                else:
                    market_cap = float(market_cap_str)

                # Write the data to the CSV file
                writer.writerow([date_str, ticker, open_price, volume, market_cap])
            else:
                print(f"1")

        print(f"Data for {date_str} has been scraped and stored successfully!")
    else:
        print(f"Failed to retrieve data for {date_str} from the website.")

# Call the function to scrape and store missing data
scrape_and_store_data()

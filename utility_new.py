import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import pandas as pd

def scrape_and_store_data():
    # Check the last date in the CSV file
    try:
        df = pd.read_csv('crypto_data.csv')
        last_date_in_file = pd.to_datetime(df['date'].iloc[-1])
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If the file doesn't exist or is empty, set the last date to 20 years ago
        last_date_in_file = datetime.now() - timedelta(days=365*20)

    # Get today's date
    today = datetime.now()

    # Calculate the number of days to scrape
    days_to_scrape = (today - last_date_in_file).days

    # Open CSV file in append mode
    with open('crypto_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)

        # Iterate over the days to scrape
        for i in range(days_to_scrape):
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
                        print("Failed to extract data from a row.")

                print(f"Data for {date_str} has been scraped and stored successfully!")
            else:
                print(f"Failed to retrieve data for {date_str} from the website.")

# Call the function to scrape and store data
scrape_and_store_data()

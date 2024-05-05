import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

def convert_datetime_format(datetime_str):
    # Parse the input datetime string into a datetime object
    input_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Format the datetime object to the desired format
    formatted_datetime = input_datetime.strftime('%Y-%m-%d:%H:00:00')

    return formatted_datetime

def scrape_and_store_data(num_days):
    # Get current datetime
    current_datetime = datetime.now()

    # List to store scraped data
    scraped_data = []

    # Iterate over each day for the specified number of days
    for day in range(num_days):
        # Calculate the date for the current iteration
        target_date = current_datetime - timedelta(days=day)

        # Iterate over each hour of the day
        for hour in range(24):
            # Calculate the datetime for the URL in the required format
            datetime_str = (datetime.combine(target_date.date(), datetime.min.time()) + timedelta(hours=hour)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Convert datetime format for storage
            formatted_datetime = convert_datetime_format(datetime_str)

            # Send a GET request to the URL
            response = requests.get(f"https://coincodex.com/historical-data/crypto/?date={datetime_str}")

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
                    close_elem = row.find(class_='close')
                    volume_elem = row.find(class_='volume')
                    market_cap_elem = row.find(class_='market-cap')

                    # Check if all elements are found
                    if ticker_elem and close_elem and volume_elem and market_cap_elem:
                        ticker = ticker_elem.text.strip()
                        close_price = close_elem.text.strip().replace('$', '').replace(',', '')
                        volume = volume_elem.text.strip().replace('$', '').replace(',', '')
                        market_cap = market_cap_elem.text.strip().replace('$', '').replace(',', '')

                        # Append the scraped data to the list
                        scraped_data.append((formatted_datetime, ticker, close_price, volume, market_cap))
                    else:
                        print("Failed to extract data from a row.")

                print(f"Data for {formatted_datetime} has been scraped.")
            else:
                print(f"Failed to retrieve data for {datetime_str} from the website.")

    # Sort the scraped data by datetime
    scraped_data.sort(key=lambda x: x[0])

    # Open CSV file in write mode
    with open('crypto_data_hourly.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the header
        writer.writerow(['Datetime', 'Ticker', 'Close Price', 'Volume', 'Market Cap'])

        # Write the sorted data to the CSV file
        writer.writerows(scraped_data)

    print("Data has been stored successfully.")

# Get the number of days from the user
num_days = int(input("Enter the number of days to scrape data for: "))

# Call the function to scrape and store data for the specified number of days
scrape_and_store_data(num_days)

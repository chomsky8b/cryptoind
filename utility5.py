import csv
from datetime import datetime
import re

def convert_data(input_file, output_file):
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        with open(output_file, 'w', newline='') as output:
            writer = csv.writer(output)
            writer.writerow(['Timestamp', 'Ticker', 'Open Price', 'Volume', 'Market Cap'])  # Write header row
            for row in reader:
                date, ticker, open_price, volume, market_cap = row
                timestamp = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S.%f')
                
                # Check if volume, market_cap, and open_price values are not empty
                if volume.strip():
                    # Remove the non-breaking space and convert the volume
                    if volume.endswith('M'):
                        volume = float(volume.replace('\u202f', '').replace('M', '')) * 1000000
                    elif volume.endswith('B'):
                        volume = float(volume.replace('\u202f', '').replace('B', '')) * 1000000000
                    else:
                        volume = float(volume.replace('\u202f', ''))
                else:
                    volume = 0  # Assign a default value for empty volume

                if market_cap.strip():
                    # Handle the market cap value with 'T', 'B', or 'M' suffix
                    if market_cap.endswith('T'):
                        market_cap = float(market_cap.replace('\u202f', '').replace('T', '')) * 1000000000000
                    elif market_cap.endswith('B'):
                        market_cap = float(market_cap.replace('\u202f', '').replace('B', '')) * 1000000000
                    elif market_cap.endswith('M'):
                        market_cap = float(market_cap.replace('\u202f', '').replace('M', '')) * 1000000
                    else:
                        market_cap = float(market_cap)
                else:
                    market_cap = 0  # Assign a default value for empty market_cap
                
                if open_price.strip():
                    # Remove non-numeric characters from the open price and convert to float
                    open_price = float(re.sub(r'[^\d\.]', '', open_price))
                else:
                    open_price = 0  # Assign a default value for empty open_price
                
                writer.writerow([timestamp, ticker, open_price, volume, market_cap])

convert_data('crypto_data.csv', 'converted_data.csv')

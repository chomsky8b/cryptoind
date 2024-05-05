import csv
from polygon import RESTClient
from datetime import datetime, timedelta

def main():
    # Ask the user for the symbol, price, and expiry of an option
    underlying = input("Please enter the underlying symbol of the option: ")
    strike_price = input("Please enter the strike price of the option: ")
    option_type = input("Please enter the type of the option (call or put): ").lower()

    # Ask the user for the number of days of data to fetch
    n_days = int(input("Please enter the number of days of data to fetch: "))

    # Calculate the start and end dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)

    # Construct the option symbol
    # Note: This is just an example. You'll need to adjust this line to match the format used by your data provider.
    symbol = f"O:{underlying}{end_date.strftime('%Y%m%d')}{option_type[0].upper()}{strike_price.replace('.', '')}"

    client = RESTClient("ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE")
    aggs = []

    # Fetch the aggregate price data for the given option
    for a in client.list_aggs(symbol, 1, "minute", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), limit=50000):
        aggs.append(a)

    # Write data to a CSV file
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Hour", "Minute", "Open", "High", "Low", "Close", "Volume"])  # Write the header

        # Write the data
        for agg in aggs:
            timestamp = datetime.fromtimestamp(agg.timestamp / 1000)  # Convert timestamp to datetime object
            date = timestamp.strftime('%Y-%m-%d')  # Extract date
            hour = timestamp.strftime('%H')  # Extract hour
            minute = timestamp.strftime('%M')  # Extract minute
            writer.writerow([date, hour, minute, agg.open, agg.high, agg.low, agg.close, agg.volume])

if __name__ == "__main__":
    main()

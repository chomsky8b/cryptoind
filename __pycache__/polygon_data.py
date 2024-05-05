import csv
from polygon import RESTClient
from datetime import datetime

def main():
    client = RESTClient("ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE")
    aggs = []

    for a in client.list_aggs("AAPL", 1, "minute", "2022-01-01", "2023-02-03", limit=50000):
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

import csv
from polygon import RESTClient
from datetime import datetime

# API key injected below for easy use. If not provided, the script will attempt
# to use the environment variable "POLYGON_API_KEY".
client = RESTClient("ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE")  # POLYGON_API_KEY environment variable is used

aggs = []
for a in client.list_aggs(
    "O:SPY240524C00515000",                         # "O:SPY251219C00650000",
    1,
    "day",
    "2024-04-01",
    "2024-05-04",
    limit=50000,
):
    aggs.append(a)

# Write data to a CSV file
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])  # Write the header

    # Write the data
    for agg in aggs:
        timestamp = datetime.fromtimestamp(agg.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')  # Convert timestamp to datetime object and format it as a string
        writer.writerow([timestamp, agg.open, agg.high, agg.low, agg.close, agg.volume])

print("Data has been written to output.csv")

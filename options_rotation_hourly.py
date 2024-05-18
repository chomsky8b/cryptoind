import csv
from polygon import RESTClient
from datetime import datetime, timedelta

# API key injected below for easy use. If not provided, the script will attempt
# to use the environment variable "POLYGON_API_KEY".
client = RESTClient("ELKyuDIy2c3CSW3eHCnuFhkq2yFmgMoE")  # POLYGON_API_KEY environment variable is used

# Option contracts
contracts = ["O:SPY2405248C00515000"] # Add more contracts as needed

for contract in contracts:
    # Extract the expiration date from the contract name
    expiration_date_str = contract[5:11]  # Extract the date string
    expiration_date = datetime.strptime(expiration_date_str, '%d%m%y')

    # Calculate the start and end dates
    end_date = min(datetime.now(), expiration_date)
    start_date = (expiration_date - timedelta(days=120)).strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    aggs = []
    for a in client.list_aggs(
        contract,                         # "O:SPY251219C00650000",
        1,
        "hour",                           # Change timespan to "hour"
        start_date,
        end_date,
        limit=50000,
    ):
        aggs.append(a)

    # Write data to a CSV file
    with open(f'{contract}_output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume", "Days to Expiration"])  # Add new column header

        # Write the data
        for agg in aggs:
            timestamp = datetime.fromtimestamp(agg.timestamp / 1000)  # Convert timestamp to datetime object
            days_to_expiration = (expiration_date - timestamp).days  # Calculate days to expiration
            writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), agg.open, agg.high, agg.low, agg.close, agg.volume, days_to_expiration])

    print(f"Data for {contract} has been written to {contract}_output.csv")

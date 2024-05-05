import pandas as pd
import yfinance as yf
import datetime

def download_spy_data(source):
    # Define the SPY ticker symbol
    spy_ticker = "SPY"

    # Set the date range for the last month
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)

    if source == 1:
        # Download data from Cboe DataShop Option EOD Summary
        spy_data = yf.download(spy_ticker, start=start_date, end=end_date)
    elif source == 2:
        # Download data from Yahoo! Finance
        spy_data = yf.download(spy_ticker, start=start_date, end=end_date, progress=False)
    elif source == 3:
        # Download data from Historical Option Data
        spy_data = yf.download(spy_ticker, start=start_date, end=end_date, progress=False)

    # Save data to a CSV file
    spy_data.to_csv(f"SPY_data_source_{source}.csv")
    print(f"SPY data from source {source} saved to SPY_data_source_{source}.csv")

# Let the user choose the data source (1, 2, or 3)
selected_source = int(input("Select data source (1: Cboe DataShop, 2: Yahoo! Finance, 3: Historical Option Data): "))
download_spy_data(selected_source)

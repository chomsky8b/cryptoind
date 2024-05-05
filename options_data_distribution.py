import pandas as pd
import yfinance as yf
import datetime

def download_spy_option_data(strikes, types):
    # Define the SPY ticker symbol
    spy_ticker = "SPY"

    # Get the SPY ticker object
    ticker = yf.Ticker(spy_ticker)

    # Get the list of expiration dates
    exp_dates = ticker.options

    # Initialize a DataFrame to store the options data
    options_data = pd.DataFrame()

    # Download options data for each strike and type
    for strike, option_type in zip(strikes, types):
        # Get the options chain for the nearest expiration date
        options_chain = ticker.option_chain(exp_dates[0])

        if option_type == 'call':
            options = options_chain.calls
        elif option_type == 'put':
            options = options_chain.puts

        # Filter the options data for the given strike price
        options_strike = options[options['strike'] == strike]

        # Append the options data to the DataFrame
        options_data = pd.concat([options_data, options_strike])

    # Format the 'lastTradeDate' column to a more readable format
    options_data['lastTradeDate'] = pd.to_datetime(options_data['lastTradeDate']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Format the numerical data to have 2 decimal places
    numerical_columns = ['lastPrice', 'bid', 'ask', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']
    options_data[numerical_columns] = options_data[numerical_columns].round(2)

    # Save data to a CSV file
    options_data.to_csv("SPY_options_data.csv")
    print("SPY options data saved to SPY_options_data.csv")

# Define the strike prices and types
strikes = [515, 505, 495, 450]
types = ['call', 'call', 'put', 'put']

# Download the options data
download_spy_option_data(strikes, types)

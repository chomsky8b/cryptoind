import pandas as pd
import matplotlib.pyplot as plt

# Option contracts
contracts = ["O:SPY240524C00505000"] #, "O:SPY240524C00520000", "O:SPY240524C00525000"]  # Add more contracts as needed

for contract in contracts:
    # Read the data from the CSV file
    data = pd.read_csv(f'{contract}_output.csv')

    # Combine all OHLC prices
    ohlc_prices = pd.concat([data['Open'], data['High'], data['Low'], data['Close']])

    # Generate a histogram for all OHLC prices
    plt.figure(figsize=(10, 6))
    plt.hist(ohlc_prices, bins=50, color='blue', edgecolor='black')
    plt.title(f'Histogram of OHLC Prices for {contract}')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig(f'{contract}_OHLC_histogram.png')  # Save the histogram as a PNG file
    plt.close()  # Close the plot

print("Histograms have been saved as PNG files.")

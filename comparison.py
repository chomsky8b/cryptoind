import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gradio as gr
import plotly.graph_objs as go

# Calculate daily returns
def calculate_daily_returns(index_series):
    daily_returns = index_series.pct_change()
    return daily_returns

# Calculate cumulative returns
def calculate_cumulative_returns(daily_returns):
    cumulative_returns = (1 + daily_returns).cumprod()
    return cumulative_returns


# Define function to calculate dates
def calc_dates(date: datetime = datetime.now()) -> tuple:
    this_year = date - timedelta(days=date.day-1)
    one_year = this_year + timedelta(days=-365)
    return (one_year.strftime("%Y-%m-%d"), this_year.strftime("%Y-%m-%d"))

# Function to fetch cryptocurrency data from CSV
def fetch_crypto_data(start_date, end_date, csv_file='crypto_data.csv'):
    try:
        print(f"Fetching data from CSV file '{csv_file}' for the period {start_date} to {end_date}.")
        data = pd.read_csv(csv_file)
        print(f"CSV file '{csv_file}' loaded successfully.")
        data['date'] = pd.to_datetime(data['date'])
        data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
        print(f"Data filtered for the period {start_date} to {end_date}.")
        return data
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error in fetch_crypto_data function: {e}")
        return pd.DataFrame()

# Function to fetch Bitcoin data from CSV
def fetch_bitcoin_data(start_date, end_date, csv_file='crypto_data.csv'):
    try:
        print(f"Fetching Bitcoin data from CSV file '{csv_file}' for the period {start_date} to {end_date}.")
        data = pd.read_csv(csv_file)
        print(f"CSV file '{csv_file}' loaded successfully.")
        data['date'] = pd.to_datetime(data['date'])
        data = data[(data['date'] >= start_date) & (data['date'] <= end_date) & (data['ticker'] == 'BTC')]  # Filter by ticker
        print(f"Bitcoin data filtered for the period {start_date} to {end_date}.")
        return data.set_index('date')  # Set index to 'date'
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error in fetch_bitcoin_data function: {e}")
        return pd.DataFrame()

# Function to plot index prices
def plot_index_prices(start_date, end_date):
    try:
        print(f"Fetching cryptocurrency data for the period {start_date} to {end_date}.")
        cryptodf = fetch_crypto_data(start_date=start_date, end_date=end_date)
        if cryptodf.empty:
            print("No data available for plotting.")
            return None

        print("Calculating crypto index.")
        index_series, _ = get_crypto_index(cryptodf)

        if index_series is None:
            print("No index value calculated.")
            return None

        # Create Plotly line plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=index_series.index, y=index_series, mode='lines', name='Cryptocurrency Index', line=dict(color='green')))

        fig.update_layout(title='Cryptocurrency Index', xaxis_title='Date', yaxis_title='Index Value')
        return fig
    except Exception as e:
        print(f"Error in plot_index_prices function: {e}")
        return None

# Function to calculate cryptocurrency index
def get_crypto_index(crypto_data):
    try:
        indict = {}
        weightdict = []
        for date, group in crypto_data.groupby('date'):
            top_20 = group.nlargest(20, "volume").reset_index(drop=True)
            w = np.sqrt(top_20['marketcap'])
            weightdf = pd.DataFrame(w / top_20["open"] / 1000)
            weightdf["date"] = date
            weightdf["ticker"] = top_20["ticker"]
            weightdf["total_cap"] = w / 1000
            weightdf.columns = ["weight", "date", "ticker", "total_cap"]
            weightdict.append(weightdf)
            indict[date] = np.sum(w)

        index_series = pd.Series(indict)
        index_series.name = "index"
        weight_data = pd.concat(weightdict, ignore_index=True)
        return index_series, weight_data
    except Exception as e:
        print(f"Error in get_crypto_index function: {e}")
        return None, None

# Calculate cumulative returns of Bitcoin
def calculate_bitcoin_cumulative_returns(bitcoin_data, index_cumulative_returns):
    try:
        if bitcoin_data.empty:
            return pd.Series()  # Return an empty series if bitcoin_data is empty
        
        # Sort Bitcoin data based on index dates
        bitcoin_data_sorted = bitcoin_data.loc[index_cumulative_returns.index]

        daily_returns = bitcoin_data_sorted['open'].pct_change()
        cumulative_returns = (1 + daily_returns).cumprod()
        print("Bitcoin cumulative returns:")
        print(cumulative_returns.head())  # Debugging print statement
        return cumulative_returns
    except Exception as e:
        print(f"Error in calculate_bitcoin_cumulative_returns function: {e}")
        return pd.Series()

# Function to plot cumulative returns
def plot_cumulative_returns(index_cumulative_returns, bitcoin_cumulative_returns):
    try:
        # Normalize both series to start from 1
        index_normalized = index_cumulative_returns / index_cumulative_returns.iloc[0]
        bitcoin_normalized = bitcoin_cumulative_returns / bitcoin_cumulative_returns.iloc[0]

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=index_normalized.index, y=index_normalized, mode='lines', name='Cryptocurrency Index'))
        fig1.update_layout(title='Cryptocurrency Index Cumulative Returns', xaxis_title='Date', yaxis_title='Cumulative Returns')

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=bitcoin_normalized.index, y=bitcoin_normalized, mode='lines', name='Bitcoin'))
        fig2.update_layout(title='Bitcoin Cumulative Returns', xaxis_title='Date', yaxis_title='Cumulative Returns')

        return fig1, fig2
    except Exception as e:
        print(f"Error in plot_cumulative_returns function: {e}")
        return None, None

# Function to save cumulative returns to CSV
def save_to_csv(data, filename):
    try:
        data.to_csv(filename, index=True)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")

# Function to generate graph with Bitcoin cumulative returns
def make_graph_with_bitcoin(start_date=None, end_date=None):
    try:
        print(f"Generating graph with start date: {start_date}, end date: {end_date}.")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Fetch cryptocurrency data and Bitcoin data
        cryptodf = fetch_crypto_data(start_date, end_date)
        bitcoin_data = fetch_bitcoin_data(start_date, end_date)

        print("Cryptocurrency data:")
        print(cryptodf.head())
        print("Bitcoin data:")
        print(bitcoin_data.head())

        if cryptodf.empty or bitcoin_data.empty:
            print("No data available for plotting.")
            return None, None, None, None  # Return None for both plots if data is not available

        # Calculate cryptocurrency index
        index_series, _ = get_crypto_index(cryptodf)

        if index_series is None:
            print("No index value calculated.")
            return None, None, None, None

        # Calculate cryptocurrency index cumulative returns
        index_daily_returns = calculate_daily_returns(index_series)
        index_cumulative_returns = calculate_cumulative_returns(index_daily_returns)

        # Calculate Bitcoin cumulative returns
        bitcoin_cumulative_returns = calculate_bitcoin_cumulative_returns(bitcoin_data, index_cumulative_returns)

        # Plot cryptocurrency index and Bitcoin cumulative returns
        fig_index = plot_index_prices(start_date, end_date)
        fig_index_cumulative, fig_bitcoin_cumulative = plot_cumulative_returns(index_cumulative_returns, bitcoin_cumulative_returns)

        # Save cumulative returns to CSV files
        save_to_csv(index_cumulative_returns, f'index_cumulative_returns_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv')
        save_to_csv(bitcoin_cumulative_returns, f'bitcoin_cumulative_returns_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv')

        return fig_index, fig_index_cumulative, fig_bitcoin_cumulative, index_cumulative_returns, bitcoin_cumulative_returns
    except Exception as e:
        print(f"Error in make_graph_with_bitcoin function: {e}")
        return None, None, None, None, None

# Main function
if __name__ == "__main__":
    make_graph_flex = make_graph_with_bitcoin
    with gr.Blocks() as iface:
        start_date_default = "2014-01-01"
        end_date_default = datetime.now().strftime("%Y-%m-%d")

        startdatebox = gr.Textbox(label=f"Start Date (YYYY-MM-DD, default: {start_date_default})", value=start_date_default)
        enddatebox = gr.Textbox(label=f"End Date (YYYY-MM-DD, default: {end_date_default})", value=end_date_default)

        index_plot = gr.Plot()
        index_cumulative_plot = gr.Plot()
        bitcoin_cumulative_plot = gr.Plot()

        update_button = gr.Button("Update Graph")

        update_button.click(fn=make_graph_flex, inputs=[startdatebox, enddatebox], outputs=[index_plot, index_cumulative_plot, bitcoin_cumulative_plot])

        iface.launch(share=True)

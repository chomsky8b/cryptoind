import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gradio as gr
import plotly.graph_objs as go

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

# Function to calculate cryptocurrency index
def get_crypto_index(crypto_data, howmany=20):
    try:
        valdict = {}
        dfdict = {}
        vallist = []
        stable_coins = ['USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'GUSD', 'USDP', 'HUSD', 'PAX', 'UST']
        crypto_data = crypto_data[~crypto_data['ticker'].isin(stable_coins)]
        crypto_data = crypto_data.sort_values('volume', ascending=False).head(howmany)
        index_value = np.sqrt(crypto_data['marketcap']).sum()
        return index_value
    except Exception as e:
        print(f"Error in get_crypto_index function: {e}")
        return None

# Function to plot index prices
def plot_index_prices(start_date, end_date):
    try:
        print(f"Fetching cryptocurrency data for the period {start_date} to {end_date}.")
        cryptodf = fetch_crypto_data(start_date=start_date, end_date=end_date)
        if cryptodf.empty:
            print("No data available for plotting.")
            return None
        
        print("Calculating crypto index.")
        index_values = cryptodf.groupby('date').apply(get_crypto_index)
        
        if index_values is None:
            print("No index value calculated.")
            return None
        
        # Fetch BTC price data
        btc_data = cryptodf[cryptodf['ticker'] == 'BTC']
        
        # Normalize data
        index_values_norm = (index_values - index_values.min()) / (index_values.max() - index_values.min())
        btc_data_norm = (btc_data['open'] - btc_data['open'].min()) / (btc_data['open'].max() - btc_data['open'].min())
        
        # Create Plotly line plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=index_values.index, y=index_values_norm, mode='lines', name='Cryptocurrency Index', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=btc_data['date'], y=btc_data_norm, mode='lines', name='BTC Price', line=dict(color='blue')))
        
        fig.update_layout(title='Normalized Cryptocurrency Index and BTC Price Comparison', xaxis_title='Date', yaxis_title='Normalized Value')
        return fig
    except Exception as e:
        print(f"Error in plot_index_prices function: {e}")
        return None

# Function to generate graph
def make_graph(start_date=None, end_date=None):
    try:
        print(f"Generating graph with start date: {start_date}, end date: {end_date}.")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        fig = plot_index_prices(start_date, end_date)
        return gr.Plot(fig)
    except Exception as e:
        print(f"Error in make_graph function: {e}")
        return None

# Main function
if __name__ == "__main__":
    make_graph_flex = make_graph
    with gr.Blocks() as iface:
        start_date_default = "2014-01-01"
        end_date_default = datetime.now().strftime("%Y-%m-%d")
        
        startdatebox = gr.Textbox(label=f"Start Date (YYYY-MM-DD, default: {start_date_default})", value=start_date_default)
        enddatebox = gr.Textbox(label=f"End Date (YYYY-MM-DD, default: {end_date_default})", value=end_date_default)
        update_button = gr.Button("Update Graph")

        theplot = gr.Plot()

        update_button.click(fn=make_graph_flex, inputs=[startdatebox, enddatebox], outputs=[theplot])

        iface.launch(share=True)

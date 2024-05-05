import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gradio as gr
import plotly.graph_objs as go

# Define function to calculate dates and plot cumulative returns
def calc_dates(start_date: str = datetime.now().strftime("%Y-%m-%d"), end_date: str = datetime.now().strftime("%Y-%m-%d")) -> tuple:
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Fetch cumulative returns data
    index_cumulative_filename = 'index_cumulative_returns.csv'
    bitcoin_cumulative_filename = 'bitcoin_cumulative_returns.csv'
    index_cumulative_returns = fetch_cumulative_returns(index_cumulative_filename)
    bitcoin_cumulative_returns = fetch_cumulative_returns(bitcoin_cumulative_filename)
    
    # Filter data based on selected dates
    index_data = index_cumulative_returns.loc[start_date_dt:end_date_dt]
    bitcoin_data = bitcoin_cumulative_returns.loc[start_date_dt:end_date_dt]
    
    # Plot cumulative returns
    index_plot = plot_cumulative_returns(index_data, 'Cryptocurrency Index')
    bitcoin_plot = plot_cumulative_returns(bitcoin_data, 'Bitcoin')
    
    return (index_plot, bitcoin_plot)

# Function to fetch cumulative returns data from CSV
def fetch_cumulative_returns(filename):
    try:
        print(f"Fetching data from CSV file '{filename}'.")
        data = pd.read_csv(filename)
        print(f"CSV file '{filename}' loaded successfully.")
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date')
        return data
    except FileNotFoundError:
        print(f"CSV file '{filename}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error in fetch_cumulative_returns function: {e}")
        return pd.DataFrame()

# Function to plot cumulative returns
def plot_cumulative_returns(data, title):
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['cumulative_returns'], mode='lines', name=title))
        fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Cumulative Returns')
        return fig
    except Exception as e:
        print(f"Error in plot_cumulative_returns function: {e}")
        return None

# Main function
if __name__ == "__main__":
    iface = gr.Interface(
        fn=calc_dates,  # Set the function for input
        inputs=["text", "text"],  # Set the input type to text for start and end dates
        outputs=["plot", "plot"],  # Set the output type to plot
        title="Cryptocurrency Cumulative Returns",
        description="Enter the start and end dates (YYYY-MM-DD) to view cumulative returns."
    )

    iface.launch(share=True)

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
import socket

app = Flask(__name__)

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

def find_available_port():
    """Find an available port for the Flask application."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        fig = plot_index_prices(start_date, end_date)
        return render_template('index.html', plot=fig.to_html())
    else:
        start_date_default = "2014-01-01"
        end_date_default = datetime.now().strftime("%Y-%m-%d")
        return render_template('index.html', start_date_default=start_date_default, end_date_default=end_date_default)

if __name__ == '__main__':
    port = find_available_port()
    app.run(debug=False, port=port)

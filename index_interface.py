import gradio as gr
import plotly.express as px
from cryptoindex import *
import pandas as pd
from updater import *
from time import sleep
from functools import partial
import argparse


last_start_date = None
last_end_date = None
is_current = False
v = None
t = 0
real_time_data = None
is_historical = False

start_date = "2023-01-01"  # Replace with your desired start date
end_date = "2023-12-31"  # Replace with your desired end date
crypto_data = fetch_crypto_data(start_date, end_date)
update_weights(crypto_data)




""" def mytimer(interval=60):
    while True:
        print("Timer: ", t)
        t += 1
        sleep(interval)

threading.Thread(target=mytimer, daemon=True).start()
 """

def plot_index_prices(start_date, end_date, **kwargs):
    global last_start_date, last_end_date, is_current, v

    if start_date != last_start_date or end_date != last_end_date:
        last_start_date = start_date
        last_end_date = end_date
        is_current = False 

    if not is_current:
        cryptodf = fetch_crypto_data(start_date = start_date, end_date = end_date, **kwargs)
        v, _ = get_crypto_index(cryptodf, func = np.sqrt)
        is_current = True
    _, _, _, output = do_sharpe(v.close)
    fig = px.line(v, x=v.index, y='close', title='Index Prices')
    fig.update_xaxes(rangeslider_visible=True)
    return fig, output

def realtime_update_weighted_prices(fname="/tmp/wts.csv"):
    if should_update_weights():
        # If it's time to update the weights, spawn a thread to do so
        threading.Thread(target=update_weights, daemon=True).start()
    last_day = pd.read_csv(fname, parse_dates=["date"])
    prices = update_day(last_day)
    _, _, _, output = do_sharpe(prices, days = False)
    fig = px.line(prices, x=prices.index, y=prices.values, title='Index Today')
    return fig, output
   
def make_graph(choice, start_date = None, end_date = None, fname = "/tmp/wts.csv", **kwargs):
    if choice == "Historical":
        fig,stats = plot_index_prices(start_date, end_date, **kwargs)
        
    else:
        fig, stats =realtime_update_weighted_prices(fname)
    
    return gr.Plot(fig), gr.Markdown(stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file" , default="/tmp/wts.csv", help="Weights for realtime computation")
    parser.add_argument("--locale", default = 'global', help="the locale")
    parser.add_argument("--market_type", default = 'crypto', help="the market type")
    parser.add_argument("--share", action = "store_true", help="share the interface")
    args = parser.parse_args()
    make_graph_flex = partial(make_graph, fname = args.data_file, locale = args.locale, market_type = args.market_type)
    update_weights(fname=args.data_file, locale = args.locale, market_type = args.market_type)
    with gr.Blocks() as iface:  # Use () for context manager
    
        
        startdatebox = gr.Textbox(label="Start Date")
        enddatebox = gr.Textbox(label="End Date")
        radio = gr.Radio(choices=["Historical", "Real-time"], label="graph type")
        update_button = gr.Button("Update Graph")  # Add a button to trigger the graph update



        theplot = gr.Plot()
        thestats = gr.Markdown()
        radio.change(fn = make_graph_flex, inputs = [radio, startdatebox, enddatebox], outputs = [theplot, thestats])
        update_button.click(fn = make_graph_flex, inputs = [radio, startdatebox, enddatebox], outputs = [theplot, thestats])
        iface.launch(share=args.share)
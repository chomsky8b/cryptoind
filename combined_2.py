from polygon import RESTClient
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calc_dates(date: datetime = datetime.now()) -> tuple:
    this_year = date - timedelta(days=date.day-1)
    one_year = this_year + timedelta(days=-365)
    return (one_year.strftime("%Y-%m-%d"), this_year.strftime("%Y-%m-%d"))


def do_sharpe(ser, days=True):
    mins_in_year = 60 * 24 * 365
    days_in_year = 365
    if days:
        themean = ser.pct_change().mean() * days_in_year
        thestd = ser.pct_change().std() * np.sqrt(days_in_year)
        
    else:
        themean = ser.pct_change().mean() * mins_in_year
        thestd = ser.pct_change().std() * np.sqrt(mins_in_year)
    sharpe = themean/thestd 
    return themean, thestd, sharpe, format_output(themean, thestd, sharpe)


def format_output(mymean, mystandarddeviation, mysharpe):
    output = f"""
    | Metric             | Value                |
    |--------------------|----------------------|
    | Mean               | {mymean:.2f}         |
    | Standard Deviation | {mystandarddeviation:.2f} |
    | Sharpe-Rivin             | {mysharpe:.3f}       |
    """
    return output

import os
api_key = os.getenv("POLYGON_KEY")

import pandas as pd
from polygon import RESTClient
client = RESTClient(api_key)

def get_ticker_trade(ticker: str):
    coinname = ticker[2:-3]
    thetrade = client.get_last_crypto_trade(coinname, "USD")
    return thetrade.price

def update_df(last_day):
    last_day["price"] = last_day.ticker.map(get_ticker_trade)
    weights = last_day.weight
    return np.average(last_day.price, weights = weights)

def get_daily_bars(ticker:str, dete = datetime.now()):
    thedate = dete.strftime("%Y-%m-%d")
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="minute", from_= thedate, to=thedate, limit=50000)
    thedf = pd.DataFrame(bars)[['timestamp', "close"]]
    thedf.set_index(pd.to_datetime(thedf.timestamp, unit='ms'), inplace = True)
    thedf.drop("timestamp", axis = 1, inplace = True)
    thedf.rename({"close": ticker}, axis = 1, inplace = True)
    return thedf

def update_day(last_day, func =np.sqrt):
    dflist = []
    for ticker in last_day.ticker:
        dflist.append(get_daily_bars(ticker))
    newdf = pd.concat(dflist, axis = 1)
    oldind = newdf.index
    last_day_r = last_day.reset_index(drop=True)
    newdf_r = newdf.reset_index(drop=True)
    close_column = last_day['close']
    #newdf_r = newdf_r.div(close_column, axis=0)
    newdf_r.index = oldind

    newdf_r["indprice"] = newdf_r.apply(lambda x: np.average(x, weights=func(last_day.weight)), axis = 1)
    return newdf_r.indprice.ffill()

etfs = ['VOO','SOXL','TQQQ','LQD','HYG','QQQ', 'IVV','SPY', 'IWM', 'DJI', 'IXIC', 'VIX', 'TLT', 'IEF', 'GLD', 'SLV', 'USO', 'UNG', 
        'VXX', 'FXE', 'FXY', 'FXB', 'FXA', 'FXC', 'FXF', 'XAU', 'XAG', 'XPT', 'XPD', 'XME', 'XHB', 'XLF', 'XLY', 'XLC', 'XLI', 'XLE', 
        'XLV', 'XLP', 'XLRE', 'XLK', 'XLU', 'XLC', 'XLB', 'XITK', 'XNTK', 'XNWK', 'XNGK']
def fetch_crypto_data(start_date, end_date, *, locale = 'global', market_type = 'crypto'):
    # Generate the date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    all_data = []
    for date in dates:
        formatted_date = date.strftime('%Y-%m-%d')
        daily_data = pd.DataFrame(client.get_grouped_daily_aggs(formatted_date, locale=locale, market_type=market_type))
        all_data.append(daily_data)

    newdata =  pd.concat(all_data)
    if market_type == 'crypto':
        newdata= newdata[newdata['ticker'].str.endswith('USD')]
    elif market_type == 'stocks':
        newdata= newdata[~newdata['ticker'].isin(etfs)]
    else:
        pass
    newdata["totalvol"] =  newdata.volume*newdata.close
    newdata["totalvol2"] =  newdata.volume/newdata.close
    # Sort the data by timestamp to ensure correct EMA calculation
    newdata.sort_values(by='timestamp', inplace=True)

    # Calculate the EMA of the `totalvol` column
    # `span` is set to 30 for a 30-day EMA
    newdata['totalvol_ema'] = newdata.groupby('ticker')['totalvol'].transform(lambda x: x.ewm(span=30, adjust=False).mean())
    newdata['totalvol2_ema'] = newdata.groupby('ticker')['totalvol2'].transform(lambda x: x.ewm(span=30, adjust=False).mean())
    return newdata

# Example usage
#start_date = '2020-01-01'
#end_date = '2024-03-27'
#crypto_data = fetch_crypto_data(start_date, end_date)


def get_crypto_index(crypto_data, howmany = 20, func = lambda x: x):

    ser = pd.Series(np.ones(howmany)).map(func)
    p = pd.Series(np.ones(howmany))
    valdict = {}
    dfdict = {}
    crypto_data.sort_values('timestamp', inplace = True, ascending = True)
    for d, df in crypto_data.groupby('timestamp'):
        df = df[df.open > 0.01]
        df = df.sort_values('totalvol_ema', ascending=False).head(howmany)
        #indopen =np.average(df.open/p, weights = ser)
        indopen = np.average(df.open.values, weights=ser.values)
        #indclose =np.average(df.close/p, weights = ser)
        indclose = np.average(df.close.values, weights=ser.values)
        ser = df.totalvol_ema.map(func)
        p  = df.close
        valdict[d] = {'open': indopen, 'close': indclose}
        dfdict[d] = pd.DataFrame({'ticker':df.ticker, 'weight':ser, 'close': df.close})

    first_key = next(iter(valdict))
    del valdict[first_key]
    del dfdict[first_key]
    vals = pd.DataFrame(valdict).T
    vals.index = pd.to_datetime(vals.index, unit = 'ms')
    vallist  =[]
    for key, val in dfdict.items():
        val['date'] = pd.to_datetime(key, unit = 'ms')
        vallist.append(val)
    dfs = pd.concat(vallist)
    return vals, dfs

def update_weights(fname="/tmp/wts.csv", **kwargs):
    start_date, end_date = calc_dates()
    crypto_data = fetch_crypto_data(start_date, end_date, **kwargs)
    _, dfs = get_crypto_index(crypto_data)
    retval = dfs[dfs.date == dfs.date.max()]
    retval.to_csv(fname, index = False)
    return retval


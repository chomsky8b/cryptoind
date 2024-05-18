# !pip install darts
# !pip install optuna

# !pip install loguru

from loguru import logger

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from darts import TimeSeries as ts
from darts.utils.missing_values import fill_missing_values as fill_missing
from dateutil.relativedelta import relativedelta
from darts.models import ExponentialSmoothing, ARIMA, AutoARIMA, Prophet, Theta, FFT, NBEATSModel, NHiTSModel, TSMixerModel
import torch
torch.set_float32_matmul_precision('medium')
from darts.metrics import mape
import optuna
from tqdm import tqdm

def sharpe(ser):
    try:
        return ser.mean()/ser.std()
    except:
        return -1

def custom_sign(series, tolerance=1e-6):
  return np.where(np.abs(series) < tolerance, 0, np.sign(series))

class MyModeler:
  def __init__(self, data, modelfile, *, initialize_model = True, window = 100, horizon = 30, resample_rate = '1s', n_epochs = 5,  modeltype = NHiTSModel,  **modelparams):
    self.data = data
    self.model_file = modelfile
    self.window = window
    self.horizon = horizon
    self.n_epochs = n_epochs
    self.fcast = {}
    self.fcastdf = {}
    self.mape = {}
    self.datadict = {}
    self.netrets = {}
    self.grossrets = {}
    self.resample_rate= resample_rate
    self.modeltype = modeltype
    self.modelparams = modelparams

    self.init_model()

  def init_model(self):

    try:
    # Attempt to load existing model
      model_path = self.model_file
      self.model = self.modeltype.load(path=model_path)
    except FileNotFoundError:
      # If model does not exist, initialize a new one
      self.model = self.modeltype(
          input_chunk_length=self.window,
          output_chunk_length=2 * self.horizon,
          random_state=42,
          n_epochs=self.n_epochs,
          **self.modelparams,
         #num_workers = 15
      )

  def day_fit(self, *, data = None, theday = None):
    if data is None:
      data = self.data
    if theday is not None:
      subdata = data[data.index.normalize() == pd.to_datetime(theday)]
    else:
      subdata = data
    targetts  = ts.from_dataframe(subdata, freq = self.resample_rate)


    #if os.path.exists(self.modelfile + '.ckpt'):
    # self.model = NHiTSModel.load_from_checkpoint(self.modelfile + '.ckpt')
    #self.model = NHiTSModel.load(self.modelfile)
    self.model.fit(targetts, verbose=True)
    self.model.save(self.model_file)

  def day_predict(self, *, data = None, theday = None):
    if data is None:
      data = self.data
    if theday is not None:
      subdata = data[data.index.normalize() == pd.to_datetime(theday)]
    else:
      subdata = data
    targetts  = ts.from_dataframe(subdata, freq = self.resample_rate)
    historical_fcast = self.model.historical_forecasts(
         targetts,
         #past_covariates = [testc],
         retrain=False, verbose=True,
        )
    fcast_mape = mape(historical_fcast, targetts)
    return historical_fcast, fcast_mape

  @logger.catch
  def fit_span(self, beg_day = None, end_day = None):
    if beg_day is None:
      if end_day is None:
        subdata = self.data
      else:
        subdata = self.data.loc[:end_day]
    else:
      if end_day is None:
        subdata = self.data.loc[beg_day:]
      else:
        subdata = self.data.loc[beg_day:end_day]

    for d, df in subdata.groupby(subdata.index.date):
      logger.info(d)
      self.datadict[d] = subdata
      self.day_fit(data = df)

  @logger.catch
  def pred_span(self, beg_day = None, end_day = None, do_pl = False, **kwargs):
    if beg_day is None:
      if end_day is None:
        subdata = self.data
      else:
        subdata = self.data.loc[:end_day]
    else:
      if end_day is None:
        subdata = self.data.loc[beg_day:]
      else:
        subdata = self.data.loc[beg_day:end_day]


    for d, df in subdata.groupby(subdata.index.date):
      logger.info(d)
      self.datadict[d] = subdata
      f, m = self.day_predict(data = df)
      self.fcast[d] = f
      fdf = f.univariate_component(0).pd_dataframe()
      self.fcastdf[d] = fdf
      self.mape[d] = m
      if do_pl:
        self.do_pl(d, **kwargs)

  def do_pl(self, d, tolerance, tcosts):
    forecast_df = self.fcastdf[d]
    actual_df = self.datadict[d]
    # Assuming `actual_df` and `forecast_df` are your DataFrame variables
    actual_df.index = actual_df.index.tz_localize(None)  # Remove timezone, making it timezone-naive
    forecast_df.index = forecast_df.index.tz_localize(None)  # Remove timezone, making it timezone-naive

    custom_df = forecast_df.diff(self.horizon).apply(lambda x: custom_sign(x, tolerance))
    investment_returns = actual_df.diff(self.horizon) * custom_df/self.horizon
    investment_returns.dropna(inplace=True)
    net_returns = investment_returns - (tcosts / self.horizon) * (investment_returns != 0.0)
    total_netto = net_returns.sum()/self.horizon
    total_brutto = investment_returns.sum()/self.horizon

    self.netrets[d] = total_netto
    self.grossrets[d] = total_brutto

# /Users/gm8b/Downloads

# mymod = MyModeler(qqqdf, modelfile = '/Users/gm8b/Downloads', window = 600, horizon=200, modeltype = NHiTSModel, save_checkpoints = True, force_reset = True)   

# #qqqdf.csv

# mymod.fit_span(beg_day = '2023-12-01',end_day = '2023-12-31')

# mymod.pred_span(do_pl=True, beg_day = '2024-01-01', end_day='2024-05-10',tolerance = 0.0002, tcosts = 0.00005)

# import pandas as pd
# from my_module import MyModeler  # Ensure to import MyModeler from the correct module if it's defined in another file

# Read the CSV file into a pandas DataFrame
data_path = 'filtered_qqqdf.csv'
qqqdf = pd.read_csv(data_path, index_col=0, parse_dates=True)

# Initialize the MyModeler class with the DataFrame and other parameters
mymod = MyModeler(
    data=qqqdf,
    modelfile='nhits_model',  # Save the model with a specific name, e.g., 'nhits_model'
    window=600,
    horizon=200,
    modeltype=NHiTSModel,
    save_checkpoints=True,
    force_reset=True
)

# Fit the model on a span of dates
mymod.fit_span(beg_day='2023-12-01', end_day='2023-12-31')

# # Predict and calculate P&L on a span of dates
mymod.pred_span(do_pl=True, beg_day='2024-01-10', end_day='2024-01-15', tolerance=0.0002, tcosts=0.00005)

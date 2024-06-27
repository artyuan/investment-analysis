import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
#from utils import stock_list
from tqdm import tqdm
from codetiming import Timer
from joblib import Parallel, delayed
from datetime import datetime
from app.utils import stock_list

def get_rsi_strategy(ind, high_threshold):
  ref_list = []
  for i in range(len(ind)):
    lower_rsi = True if ind[i] < 30 else False
    high_rsi = True if ind[i] > high_threshold else False

    if len(ref_list) == 0:
      ref_list.append(lower_rsi)
      n=0
    else:
      if high_rsi:
        ref_list.append(False)

      elif ref_list[-1] == True:
        lower_rsi = ref_list[-1]
        ref_list.append(lower_rsi)
      else:
        ref_list.append(lower_rsi)
      n+=1

  return ref_list
def get_stock_signal_2(ticker):
    df = pd.DataFrame()
    df = df.ta.ticker(f"{ticker}.SA")

    MyStrategy = ta.Strategy(
        name="DCSMA10",
        ta=[
            {"kind": "sma", "length": 10},
            {"kind": "sma", "length": 10},
            {"kind": "sma", "length": 20},
            {"kind": "sma", "length": 20},
            {"kind": "sma", "length": 50},
            {"kind": "sma", "length": 100},
            {"kind": "sma", "length": 200},
            {"kind": "ema", "length": 10},
            {"kind": "ema", "length": 20},
            {"kind": "ema", "length": 20},
            {"kind": "ema", "length": 50},
            {"kind": "ema", "length": 100},
            {"kind": "ema", "length": 200},
            {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
            {"kind": "rsi", "length": 14, "scalar": 100},
            {"kind": "bbands"},
            {"kind": "kc"},
            {"kind": "obv"},
            {"kind": "ad"},
            {"kind": "stoch"},
            {"kind": "stochrsi"},
        ]
    )

    # (2) Run the Strategy
    df.ta.strategy(MyStrategy)
    df = df.iloc[[-1]]

    df_filter = df.iloc[[-1]].copy()
    price = df_filter['Close'].values[0]
    df_filter = df_filter.reset_index()
    rsi_lst = df_filter['RSI_14'].values.tolist()
    rsi_results = get_rsi_strategy(rsi_lst, 70)
    rsi_results_2 = get_rsi_strategy(rsi_lst, 50)

    # Basic strategies
    ## RSI
    df_filter['strategy_rsi_70'] = rsi_results
    df_filter['strategy_rsi_50'] = rsi_results_2
    ## Moving average 200
    df_filter['strategy_sma_200'] = df_filter['Close'] > df_filter['SMA_200']
    ## MACD
    df_filter['strategy_macd'] = df_filter['MACD_12_26_9'] > df_filter['MACDs_12_26_9']
    ## Golden cross
    df_filter["GC"] = df_filter['SMA_20'] > df_filter['SMA_50']

    # Combinations
    df_filter['strategy_sma_200_rsi'] = df_filter.apply(
        lambda x: True if (x['strategy_sma_200'] == True) & (x['RSI_14'] < 70) else False, axis=1)

    df_filter["strategy_macd_rsi_50"] = df_filter.apply(
        lambda x: True if (x['RSI_14'] < 50) & (x['strategy_macd'] == True) else False, axis=1)
    df_filter["strategy_macd_rsi_70"] = df_filter.apply(
        lambda x: True if (x['RSI_14'] < 70) & (x['strategy_macd'] == True) else False, axis=1)
    df_filter["strategy_macd_gc"] = df_filter.apply(
        lambda x: True if (x['GC'] == True) & (x['strategy_macd'] == True) else False, axis=1)

    df_filter['high_trend_basic'] = df_filter[['strategy_sma_200', 'strategy_macd', 'strategy_rsi_70', 'GC']].sum(
        axis=1)
    df_filter['strategy_high_trend_basic'] = df_filter['high_trend_basic'].apply(lambda x: True if x > 3 else False)

    df_filter['high_trend_complete'] = df_filter[
        ['strategy_sma_200', 'strategy_macd', 'strategy_rsi_70', 'GC', 'strategy_rsi_50',
         'strategy_sma_200_rsi', 'strategy_macd_rsi_50', 'strategy_macd_rsi_70',
         'strategy_macd_gc']].sum(axis=1)
    df_filter['strategy_high_trend_complete'] = df_filter['high_trend_complete'].apply(
        lambda x: True if x > 5 else False)

    # Negative
    df_filter['neg_sma_200'] = df_filter['Close'] < df_filter['SMA_200']
    df_filter['neg_macd'] = df_filter['MACD_12_26_9'] < df_filter['MACDs_12_26_9']
    df_filter['neg_rsi'] = df_filter['RSI_14'] > 70
    df_filter["neg_GC"] = df_filter['SMA_20'] < df_filter['SMA_50']
    df_filter['down_trend_basic'] = df_filter[['neg_sma_200', 'neg_macd', 'neg_rsi', 'neg_GC']].sum(axis=1)

    df_filter['strategy_trend_basic'] = df_filter['high_trend_basic'] > df_filter['down_trend_basic']

    best_strategy_nm = best_stock_strategy[best_stock_strategy['ticker'] == ticker]['strategy'].values[0]
    count_stg = best_stock_strategy[best_stock_strategy['ticker'] == ticker]['count'].values[0]
    strategy_df = df_filter.ta.tsignals(df_filter[f'{best_strategy_nm}'], asbool=True, append=True)
    df_filter['Signal'] = df_filter[best_strategy_nm].values[0]
    df_filter['ticker'] = ticker
    df_filter['strategy'] = best_strategy_nm
    df_filter['price'] = price
    df_filter['init_value'] = 1000
    df_filter['count_strategies'] = count_stg
    return df_filter

if __name__ == '__main__':
    portfolio_position = pd.read_csv('../data/close_position_v2.csv')
    best_stock_strategy = pd.read_csv('../data/best_strategy.csv')
    backtest_final = pd.read_csv('../data/backtest_final.csv')
    teste = stock_list

    df_signals = pd.DataFrame()
    for ticker in tqdm(stock_list):
        ticker_signal = get_stock_signal_2(ticker)
        df_signals = pd.concat([df_signals, ticker_signal], axis=0)
    df_signals['last_updated_date'] = datetime.today().date()
    df_signals.to_csv('../data/daily_update.csv', index=False)
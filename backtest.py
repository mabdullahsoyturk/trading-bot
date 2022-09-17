import os
import sys
import time
from ohlcv import OHLCV
import ccxt
from ccxt.base.decimal_to_precision import ROUND_UP
import numpy as np
from backtesting.strategy import *

msec = 1000
minute = 60 * msec
hold = 30

exchange = ccxt.binance(
    {
        'options': {
            'defaultType': 'future',
        },
    }
)

from_datetime = '2022-09-01 00:00:00'
since = exchange.parse8601(from_datetime)

# Structure: [timestamp,     open,     high,     low,      close,    volume]
# Example  : [1659800700000, 23202.09, 23204.62, 23185.51, 23201.32, 175.31157]

all_ohlcvs = []
all_ohlcvs_data = []
while True:
    try:
        print(exchange.milliseconds(), 'Fetching candles')
        ohlcv_data = exchange.fetch_ohlcv('BTC/USDT', '30m', since=since)
        print(exchange.milliseconds(), 'Fetched', len(ohlcv_data), 'candles')

        ohlcv_data = ohlcv_data

        ohlcvs = [OHLCV(*data) for data in ohlcv_data]

        if len(ohlcv_data):
            all_ohlcvs += ohlcvs
            all_ohlcvs_data += ohlcv_data
            since = ohlcv_data[-1][0] + 1
        else:
            break
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error')

all_ohlcvs_data = np.array(all_ohlcvs_data)
short_summary = two_to_one_engulf_short(all_ohlcvs, all_ohlcvs_data)
long_summary = two_to_one_engulf_long(all_ohlcvs, all_ohlcvs_data)

print(short_summary)
print(long_summary)

long_summary.visualize()
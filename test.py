import os
import sys
import time
from ohlcv import OHLCV
import ccxt
from ccxt.base.decimal_to_precision import ROUND_UP
from strategy import two_to_one_engulf_long, two_to_one_engulf_short, macd_strategy_long, macd_strategy_short

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

num_candles = 12 * 24 * 2
timeframe = "5m"
interval = exchange.parse_timeframe(timeframe) * 1000

# Structure: [timestamp,     open,     high,     low,      close,    volume]
# Example  : [1659800700000, 23202.09, 23204.62, 23185.51, 23201.32, 175.31157]

while True:
    try:
        print(exchange.milliseconds(), 'Fetching candles')
        since = exchange.round_timeframe(timeframe, exchange.milliseconds(), ROUND_UP) - (num_candles * interval)
        ohlcv_data = exchange.fetch_ohlcv('BTC/USDT', timeframe, since=since, limit=num_candles)
        print(exchange.milliseconds(), 'Fetched', len(ohlcv_data), 'candles')

        print(len(ohlcv_data))

        ohlcvs = [OHLCV(*data) for data in ohlcv_data]
        #two_to_one_engulf_long(ohlcvs, ohlcv_data)
        #two_to_one_engulf_short(ohlcvs, ohlcv_data)
        macd_strategy_long(ohlcvs, ohlcv_data)
        macd_strategy_short(ohlcvs, ohlcv_data)

        time.sleep(500)
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

        print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
        time.sleep(hold)

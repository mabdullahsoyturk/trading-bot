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
        print(ohlcv_data)
        print(exchange.milliseconds(), 'Fetched', len(ohlcv_data), 'candles')

        print(len(ohlcv_data))

        ohlcvs = [OHLCV(*data) for data in ohlcv_data]

        if len(ohlcv_data):
            all_ohlcvs += ohlcvs
            all_ohlcvs_data += ohlcv_data
            since = ohlcv_data[-1][0] + 1
        else:
            break
        #two_to_one_engulf_long(ohlcvs, ohlcv_data)
        #two_to_one_engulf_short(ohlcvs, ohlcv_data)
        #macd_strategy_long(ohlcvs, ohlcv_data)
        #macd_strategy_short(ohlcvs, ohlcv_data)
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error')

# macd_strategy_long(all_ohlcvs, all_ohlcvs_data)
# macd_strategy_short(all_ohlcvs, all_ohlcvs_data)
short_r, short_num_stops, short_num_profits, short_num_positions = two_to_one_engulf_short(all_ohlcvs, all_ohlcvs_data)
long_r, long_num_stops, long_num_profits, long_num_positions = two_to_one_engulf_long(all_ohlcvs, all_ohlcvs_data)

print(f'\nShort r: {short_r}, Long r: {long_r}, Total r: {long_r + short_r}\n')

print(f'[Short] Win Rate: {short_num_profits/short_num_positions}, Number of Stops: {short_num_stops}, Number of Take Profits: {short_num_profits}')
print(f'[Long] Win Rate: {long_num_profits/long_num_positions}, Number of Stops: {long_num_stops}, Number of Take Profits: {long_num_profits}')

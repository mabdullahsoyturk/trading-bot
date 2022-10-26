import logging
import json
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging

#config_logging(logging, logging.DEBUG)

def get_open_interest(symbol="BTCUSDT"):
    futures_client = UMFutures()
    return futures_client.open_interest("BTCUSDT")["openInterest"]

def get_funding_rate(symbol="BTCUSDT"):
    futures_client = UMFutures()
    return futures_client.funding_rate("BTCUSDT", **{"limit": 1})

def get_long_short_account_ratio(symbol="BTCUSDT", period="5m"):
    futures_client = UMFutures()
    return futures_client.long_short_account_ratio(symbol, period)

def get_top_long_short_account_ratio(symbol="BTCUSDT", period="5m"):
    futures_client = UMFutures()
    return futures_client.top_long_short_account_ratio(symbol, period)

def get_top_long_short_position_ratio(symbol="BTCUSDT", period="5m"):
    futures_client = UMFutures()
    return futures_client.top_long_short_position_ratio(symbol, period)

def get_all_symbols():
    futures_client = UMFutures()
    symbols_info = futures_client.exchange_info()['symbols']
    symbols = [symbol['symbol'] for symbol in symbols_info]
    return symbols

if __name__ == '__main__':
    #print(json.dumps(get_top_long_short_account_ratio(), indent=4))
    #print(json.dumps(get_top_long_short_position_ratio(), indent=4))

    print(sorted(get_all_symbols()))
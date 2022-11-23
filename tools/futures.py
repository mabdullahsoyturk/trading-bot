import logging
import json
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging

futures_client = UMFutures()

def get_open_interest(symbol="BTCUSDT"):
    return futures_client.open_interest(symbol)["openInterest"]

def get_mark_price(symbol="BTCUSDT"):
    return futures_client.mark_price(symbol)["markPrice"]

def get_funding_rate(symbol="BTCUSDT"):
    futures_client = UMFutures()
    return futures_client.funding_rate(symbol, **{"limit": 1})[0]["fundingRate"]

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

    symbols = sorted(get_all_symbols())

    large_interest_symbols = {}
    threshold = 30000000 # 30M dollars

    for symbol in symbols:
        try:
            open_interest = float(get_open_interest(symbol=symbol))
            mark_price = float(get_mark_price(symbol=symbol))
            interest_in_usd = open_interest * mark_price

            funding_rate = float(get_funding_rate(symbol=symbol))

            if interest_in_usd > threshold and funding_rate > -0.2:
                large_interest_symbols[symbol] = interest_in_usd

            #print(f'[{symbol}] --> {open_interest} {symbol[:-4]}, {interest_in_usd:,} {symbol[-4:]}')
        except Exception as e:
            print(e)

    print(json.dumps(large_interest_symbols, indent=4))
import os
import sys

import ccxt

from dotenv import load_dotenv
load_dotenv()

from src.utils import get_balance, get_amount, get_x_days_ago_in_iso, create_order
from src.strategies.engulfing import EngulfingStrategy
from src.order import Order
from src.position import Position

from ohlcv import OHLCV

if __name__ == '__main__':
    try:
        exchange = ccxt.binance({
            'options': {
                    'defaultType': 'future',
            },
            'apiKey': f'{os.getenv("API_KEY")}',
            'secret': f'{os.getenv("SECRET")}',
        })

        markets = exchange.load_markets()

        response = exchange.set_leverage(1, 'BTC/USDT')
        print(response)

        from_iso = get_x_days_ago_in_iso(x=2)
        since = exchange.parse8601(from_iso)
        symbol = 'BTC/USDT'
        timeframe = '30m'
        budget = 40

        print(exchange.milliseconds(), 'Fetching candles')
        ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe, since=since)
        print(exchange.milliseconds(), 'Fetched', len(ohlcv_data), 'candles')
        ohlcvs = [OHLCV(*data) for data in ohlcv_data[-4:]]

        strategy = EngulfingStrategy(ohlcvs, ohlcv_data)

        #position = strategy.execute()
        position = Position('sell', None, ohlcvs[-1].open_price, ohlcvs[-1].open_price + 1000, ohlcvs[-1].open_price - 1000, None, None)

        if position:
            balance = get_balance(exchange)
            if balance['USDT']['free'] < 81:
                print(f'Balance ({balance}) is smaller than 80 dollars')
                exit()

            amount = get_amount(budget, position.side, position.entry_price, position.stop_loss, position.take_profit)

            params = {
                #'stopPrice': exchange.price_to_precision(symbol, position.stop_loss)
            }
            
            # Limit Order
            order = Order(symbol, "limit", position.side, amount, position.entry_price, params)
            create_order(exchange, order)

             # Stop Loss
            stopLossParams = {
                'stopPrice': exchange.price_to_precision(symbol, position.stop_loss)
            }
            inverted_side = 'sell' if position.side == 'buy' else 'buy'
            stop_loss_order = Order(symbol, "STOP_MARKET", inverted_side, amount, None, stopLossParams)
            create_order(exchange, stop_loss_order)

            # Take Profit
            takeProfitParams = {
                'stopPrice': exchange.price_to_precision(symbol, position.take_profit)
            }
            take_profit_order = Order(symbol, "TAKE_PROFIT_MARKET", inverted_side, amount, None, takeProfitParams)
            create_order(exchange, take_profit_order)
        else:
            print(f'Did not have any opportunity to open a position')
    except Exception as e:
        print(e)

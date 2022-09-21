import os
import sys
from datetime import datetime

import numpy as np

import ccxt

from dotenv import load_dotenv
load_dotenv()

from src.utils import get_balance, get_amount, get_x_days_ago_in_iso, create_order
from src.strategies.engulfing import EngulfingStrategy
from src.order import Order

from ohlcv import OHLCV

if __name__ == '__main__':
    symbol = 'BTC/USDT'
    timeframe = '30m'
    risk_in_dollars = 1

    try:
        exchange = ccxt.binance({
            'options': {
                    'defaultType': 'future',
            },
            'apiKey': f'{os.getenv("API_KEY")}',
            'secret': f'{os.getenv("SECRET")}',
        })
    except Exception as e:
        print("Couldn't connect to binance")

    #### Delete closed orders
    try:
        positions = exchange.fetch_positions([symbol])
        
        if positions[-1]['contracts'] > 0:
            print("Exiting because there is already an open position")
            exit()
        else:
            orders = exchange.fetch_open_orders(symbol)

            if len(orders) > 0:
                for order in orders:
                    canceled = exchange.cancel_order(order['id'], symbol)
                print("Cancelled all stops and take profits")
    except Exception as e:
        print(e)
        print("Error while closing old orders")

    try:
        markets = exchange.load_markets()

        response = exchange.set_leverage(1, 'BTC/USDT')

        from_iso = get_x_days_ago_in_iso(x=5)
        since = exchange.parse8601(from_iso)

        ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe, since=since)
        print(datetime.fromtimestamp(exchange.milliseconds()/1000.0), 'Fetched', len(ohlcv_data), 'candles')
        ohlcvs = [OHLCV(*data) for data in ohlcv_data[-4:]]

        balance = get_balance(exchange)
        print(f'Current Free Balance: {balance}')

        strategy = EngulfingStrategy(ohlcvs, np.array(ohlcv_data))

        position = strategy.execute()

        if position:
            try:
                amount = get_amount(balance, position.side, position.entry_price, position.stop_loss, risk=risk_in_dollars)

                params = {}
                
                ########### Limit Order ###########
                order = Order(symbol, "limit", position.side, amount, position.entry_price, params)
                limit_order = create_order(exchange, order)
                ###################################

                inverted_side = 'sell' if position.side == 'buy' else 'buy'

                if limit_order:
                    ########### Stop Loss ###########
                    stopLossParams = {
                        'stopPrice': exchange.price_to_precision(symbol, position.stop_loss)
                    }
                    
                    stop_loss_order = Order(symbol, "STOP_MARKET", inverted_side, limit_order['amount'], None, stopLossParams)
                    stop_order = create_order(exchange, stop_loss_order)
                    #################################

                    ########### Take Profit ###########
                    takeProfitParams = {
                        'stopPrice': exchange.price_to_precision(symbol, position.take_profit)
                    }
                    take_profit_order = Order(symbol, "TAKE_PROFIT_MARKET", inverted_side, limit_order['amount'], None, takeProfitParams)
                    profit_order = create_order(exchange, take_profit_order)
                    ###################################
            except Exception as e:
                print(e)
                exit()

        else:
            print(f'\nDid not have any opportunity to open a position')
    except Exception as e:
        print(e)

import os
import sys
from datetime import datetime

import numpy as np

import ccxt

from dotenv import load_dotenv
load_dotenv()

from src.utils import get_balance, get_amount, get_x_days_ago_in_iso, create_order
from src.strategies import EngulfingStrategy, MacdStrategy
from src.data import Order

from src.exchange import Exchange

SYMBOL = 'BTC/USDT'
TIMEFRAME = '30m'
RISK_IN_DOLLARS = 1

if __name__ == '__main__':
    exchange = Exchange()

    #### Delete stop and take profit orders if the position is closed
    if not exchange.position_exists(SYMBOL): 
        exchange.cancel_all_open_orders(SYMBOL)

    exchange.set_leverage(leverage=1, ticker='BTC/USDT')

    from_iso = get_x_days_ago_in_iso(x=5)
    since = exchange.iso_to_timestamp(from_iso)

    # Get data
    ohlcv_data = exchange.get_ohlcv_data(SYMBOL, TIMEFRAME, since=since)

    balance = exchange.get_free_balance()
    print(f'Current Free Balance: {balance}')

    # Run strategy
    strategy = EngulfingStrategy(ohlcv_data)
    #strategy = MacdStrategy(ohlcv_data)

    position = strategy.execute()

    if position:
        # If strategy returns a position, open it
        amount = get_amount(balance, position.side, position.entry_price, position.stop_loss, risk=RISK_IN_DOLLARS)

        params = {}
        
        ########### Limit Order ###########
        order = Order(SYMBOL, "limit", position.side, amount, position.entry_price, params)
        limit_order = exchange.create_order(order)
        ###################################

        inverted_side = 'sell' if position.side == 'buy' else 'buy'

        ########### Stop Loss ###########
        stopLossParams = {
            'stopPrice': exchange.price_to_precision(SYMBOL, position.stop_loss)
        }
        
        stop_loss_order = Order(SYMBOL, "STOP_MARKET", inverted_side, limit_order['amount'], None, stopLossParams)
        stop_order = exchange.create_order(stop_loss_order)
        #################################

        ########### Take Profit ###########
        takeProfitParams = {
            'stopPrice': exchange.price_to_precision(SYMBOL, position.take_profit)
        }
        take_profit_order = Order(SYMBOL, "TAKE_PROFIT_MARKET", inverted_side, limit_order['amount'], None, takeProfitParams)
        profit_order = exchange.create_order(take_profit_order)
        ###################################
    else:
        print(f'\nDid not have any opportunity to open a position')

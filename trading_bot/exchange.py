import os
import sys

from dotenv import load_dotenv
load_dotenv()

import ccxt

from trading_bot.utils import get_amount
from trading_bot.data import Order

class Exchange:
    """ An error safe exchange representation """
    
    def __init__(self, args):
        self.args = args
        self.exchange = self.init_exchange()
        self.exchange.load_markets()
        self.set_leverage(args.leverage)

    def init_exchange(self):
        try:
            return ccxt.binance({
                'options': {
                        'defaultType': 'future',
                },
                'apiKey': f'{os.getenv("API_KEY")}',
                'secret': f'{os.getenv("SECRET")}',
            })
        except Exception as e:
            sys.exit(f'Could not connect to binance: {e}')

    def get_ohlcv_data(self, symbol, timeframe, since_start):
        all_ohlcvs_data = []
        since = since_start
        
        try:
            while True:
                ohlcv_data = self.exchange.fetch_ohlcv(symbol, timeframe, since=since)

                if len(ohlcv_data):
                    all_ohlcvs_data += ohlcv_data
                    since = ohlcv_data[-1][0] + 1
                else:
                    break

            return all_ohlcvs_data
        except Exception as e:
            sys.exit(f'Could not get ohlcv data: {e}')

    def get_free_balance(self, asset_name="USDT"):
        try:
            return self.exchange.fetch_balance()[asset_name]["free"]
        except Exception as e:
            sys.exit(f'Could not get free balance: {e}')

    def cancel_order(self, symbol, order):
        try:
            exchange.cancel_order(order['id'], symbol)
        except Exception as e:
            sys.exit(f'Could not cancel the order: {e}')

    def cancel_all_open_orders(self, symbol):
        try:
            orders = self.exchange.fetch_open_orders(symbol)

            if len(orders) > 0:
                for order in orders:
                    canceled = self.exchange.cancel_order(order['id'], symbol)
        except Exception as e:
            sys.exit(f'Could not cancel all open orders: {e}')

    def create_order(self, order):
        try:
            opened_order = self.exchange.create_order(order.symbol, order.type, order.side, order.amount, order.price, order.params)
            print(f'An order has ben created successfully: \n\n{opened_order}')

            return opened_order
        except Exception as e:
            sys.exit(f'Could not create the order: {e}')

    def price_to_precision(self, symbol, price):
        try:
            return self.exchange.price_to_precision(symbol, price)
        except Exception as e:
            sys.exit(f'Could not create the precision: {e}')

    def position_exists(self, symbol):
        try:
            positions = self.exchange.fetch_positions([symbol])
            
            if positions[-1]['contracts'] > 0:
                return True

            return False
        except Exception as e:
            sys.exit(f'Could not fetch positions: {e}')

    def open_position(self, position):
        amount = get_amount(balance, position.side, position.entry_price, position.stop_loss, risk=self.args.risk)
        
        ########### Limit Order ###########
        params = {}

        order = Order(self.args.symbol, "limit", position.side, amount, position.entry_price, params)
        limit_order = self.create_order(order)
        ###################################

        inverted_side = 'sell' if position.side == 'buy' else 'buy'

        ########### Stop Loss Order ###########
        stop_loss_params = {
            'stopPrice': self.price_to_precision(self.args.symbol, position.stop_loss)
        }
        
        stop_loss_order = Order(self.args.symbol, "STOP_MARKET", inverted_side, limit_order['amount'], None, stop_loss_params)
        stop_order = self.create_order(stop_loss_order)
        #################################

        ########### Take Profit Order ###########
        take_profit_params = {
            'stopPrice': self.price_to_precision(self.args.symbol, position.take_profit)
        }

        take_profit_order = Order(self.args.symbol, "TAKE_PROFIT_MARKET", inverted_side, limit_order['amount'], None, take_profit_params)
        profit_order = self.create_order(take_profit_order)
        ###################################

    def set_leverage(self, leverage, ticker="BTC/USDT"):
        try:
            self.exchange.set_leverage(leverage, ticker)
        except Exception as e:
            sys.exit(f'Could not set leverage: {e}')

    def iso_to_timestamp(self, iso):
        try:
            return self.exchange.parse8601(iso)
        except Exception as e:
            sys.exit(f'Could not convert iso to timestamp: {e}')
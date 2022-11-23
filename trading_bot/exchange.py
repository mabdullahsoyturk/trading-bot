import os
import sys
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

import ccxt # type: ignore
from ccxt.binance import binance # type: ignore

from trading_bot.data import Order, Position

class Exchange:
    """ An error safe exchange representation """
    
    def __init__(self, args) -> None:
        self.args = args
        self.exchange = self.init_exchange()
        self.exchange.load_markets()
        self.set_leverage(args.leverage)

    def init_exchange(self) -> binance:
        """Initializes the exchange (Binance only for now)

        Returns:
            binance: exchange object
        """
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

    def get_ohlcv_data(self, symbol:str, timeframe:str, since_start:int) -> list:
        """Retrieves OHLCV (open,highest,lowest,close,volume) data

        Args:
            symbol (str): Symbol of the pair (e.g. BTC/USDT)
            timeframe (str): Timeframe that we use for trading (e.g. 30m)
            since_start (int): Retrieve data starting from x days ago.

        Returns:
            list: List of OHLCV data
        """
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

    def get_free_balance(self, asset_name:Optional[str]="USDT") -> float:
        """Free balance of the specified asset

        Args:
            asset_name (Optional[str], optional): Defaults to "USDT".

        Returns:
            float: Balance
        """
        try:
            return self.exchange.fetch_balance()[asset_name]["free"]
        except Exception as e:
            sys.exit(f'Could not get free balance: {e}')

    def cancel_order(self, symbol:str, order:dict) -> None:
        """Cancels the given order

        Args:
            symbol (str): Symbol of the pair (e.g. BTC/USDT)
            order (dict): Order dict returned from exchange api.
        """
        try:
            self.exchange.cancel_order(order['id'], symbol)
        except Exception as e:
            sys.exit(f'Could not cancel the order: {e}')

    def cancel_all_open_orders(self, symbol:str) -> None:
        """Cancels all open orders

        Args:
            symbol (str): Symbol of the pair (e.g. BTC/USDT)
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)

            if len(orders) > 0:
                for order in orders:
                    canceled = self.exchange.cancel_order(order['id'], symbol)
        except Exception as e:
            sys.exit(f'Could not cancel all open orders: {e}')

    def create_order(self, order: Order) -> dict:
        """Creates the given order

        Args:
            order (Order): Order object that contains info about the order

        Returns:
            dict: Opened order
        """
        try:
            opened_order = self.exchange.create_order(order.symbol, order.type, order.side, order.amount, order.price, order.params)
            print(f'An order has ben created successfully: \n\n{opened_order}')

            return opened_order
        except Exception as e:
            sys.exit(f'Could not create the order: {e}')

    def price_to_precision(self, symbol:str, price:float):
        try:
            return self.exchange.price_to_precision(symbol, price)
        except Exception as e:
            sys.exit(f'Could not create the precision: {e}')

    def position_exists(self, symbol:str) -> bool:
        try:
            positions = self.exchange.fetch_positions([symbol])
            
            if positions[-1]['contracts'] > 0:
                return True

            return False
        except Exception as e:
            sys.exit(f'Could not fetch positions: {e}')

    def open_position(self, position:Position, amount:float) -> None:
        """Opens a position along with stop loss and take profit orders

        Args:
            position (Position): Position to be opened
            amount (float): Amount of the security.
        """
        ########### Limit Order ###########
        params:dict = {}

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

    def set_leverage(self, leverage:int, symbol:Optional[str]="BTC/USDT") -> None:
        """Sets the leverage for the symbol

        Args:
            leverage (int): Margin leverage
            symbol (Optional[str], optional): Defaults to "BTC/USDT".
        """
        try:
            self.exchange.set_leverage(leverage, symbol)
        except Exception as e:
            sys.exit(f'Could not set leverage: {e}')

    def iso_to_timestamp(self, iso:str) -> int:
        """Converts iso to timestamp

        Args:
            iso (str): Date in iso format

        Returns:
            int: Date in timestamp
        """
        try:
            return self.exchange.parse8601(iso)
        except Exception as e:
            sys.exit(f'Could not convert iso to timestamp: {e}')
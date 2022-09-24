import numpy as np
import ccxt

from trading_bot.utils import get_amount, get_x_days_ago_in_iso, get_args
from trading_bot.strategies import EngulfingStrategy, MacdStrategy
from trading_bot.data import Order
from trading_bot.exchange import Exchange

if __name__ == '__main__':
    args = get_args()
    exchange = Exchange()

    #### Delete stop and take profit orders if the position is closed
    if not exchange.position_exists(args.symbol): 
        exchange.cancel_all_open_orders(args.symbol)

    exchange.set_leverage(leverage=1, ticker=args.symbol)

    from_iso = get_x_days_ago_in_iso(x=20)
    since = exchange.iso_to_timestamp(from_iso)

    # Get data
    ohlcv_data = exchange.get_ohlcv_data(args.symbol, args.timeframe, since)

    balance = exchange.get_free_balance()
    print(f'Current Free Balance: {balance}')

    # Run strategy
    strategy = EngulfingStrategy(ohlcv_data)
    #strategy = MacdStrategy(ohlcv_data)

    position = strategy.execute()

    if position:
        # If strategy returns a position, open it
        amount = get_amount(balance, position.side, position.entry_price, position.stop_loss, risk=args.risk)

        params = {}
        
        ########### Limit Order ###########
        order = Order(args.symbol, "limit", position.side, amount, position.entry_price, params)
        limit_order = exchange.create_order(order)
        ###################################

        inverted_side = 'sell' if position.side == 'buy' else 'buy'

        ########### Stop Loss ###########
        stopLossParams = {
            'stopPrice': exchange.price_to_precision(args.symbol, position.stop_loss)
        }
        
        stop_loss_order = Order(args.symbol, "STOP_MARKET", inverted_side, limit_order['amount'], None, stopLossParams)
        stop_order = exchange.create_order(stop_loss_order)
        #################################

        ########### Take Profit ###########
        takeProfitParams = {
            'stopPrice': exchange.price_to_precision(args.symbol, position.take_profit)
        }
        take_profit_order = Order(args.symbol, "TAKE_PROFIT_MARKET", inverted_side, limit_order['amount'], None, takeProfitParams)
        profit_order = exchange.create_order(take_profit_order)
        ###################################
    else:
        print(f'\nDid not have any opportunity to open a position')

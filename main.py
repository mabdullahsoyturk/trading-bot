import ccxt # type: ignore
import csv

from trading_bot.utils import get_x_days_ago_in_iso, get_args, get_amount
from trading_bot.strategies import EngulfingStrategy, MacdStrategy
from trading_bot.exchange import Exchange
from trading_bot.backtest import Backtester

if __name__ == '__main__':
    args = get_args()
    exchange = Exchange(args)

    # Cancel all stop and take profit orders if there is no open position
    if not exchange.position_exists(args.symbol): 
        exchange.cancel_all_open_orders(args.symbol)

    # Get timestamp for the start date
    from_iso = get_x_days_ago_in_iso(x=args.days_ago)
    since = exchange.iso_to_timestamp(from_iso)

    # Get data
    ohlcv_data = exchange.get_ohlcv_data(args.symbol, args.timeframe, since)

    # Get account balance
    balance = exchange.get_free_balance()

    # Initialize strategy
    strategy = EngulfingStrategy(ohlcv_data, args)

    # Backtest
    if args.backtest:
        backtester = Backtester(strategy, args, balance)
        backtester()
        exit()

    # Run strategy
    position = strategy.execute()

    # If strategy suggests a position, open it.
    if position:
        # Get the amount of security that you need to long or short according to your risk
        # Returns None if balance is not enough or amount is lower than minimum position amount
        amount, leverage = get_amount(balance, position.side, position.entry_price, position.stop_loss, risk=args.risk)

        if amount:
            exchange.set_leverage(leverage)
            exchange.open_position(position, amount)

        # Append the opened position to the output csv file
        if args.export and amount:
            with open(args.export_path + "/opened_positions.csv", 'a') as export_file:
                csv_writer = csv.writer(export_file, delimiter=',')
                csv_writer.writerow(position.__repr__())

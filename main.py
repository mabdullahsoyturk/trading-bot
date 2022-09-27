import ccxt # type: ignore

from trading_bot.utils import get_x_days_ago_in_iso, get_args
from trading_bot.strategies import EngulfingStrategy, MacdStrategy
from trading_bot.exchange import Exchange

if __name__ == '__main__':
    args = get_args()
    exchange = Exchange(args)

    # Cancel stop and take profit orders if the position is closed
    if not exchange.position_exists(args.symbol): 
        exchange.cancel_all_open_orders(args.symbol)

    # Get timestamp for the start date
    from_iso = get_x_days_ago_in_iso(x=args.days_ago)
    since = exchange.iso_to_timestamp(from_iso)

    # Get data
    ohlcv_data = exchange.get_ohlcv_data(args.symbol, args.timeframe, since)

    # Initialize strategy
    strategy = EngulfingStrategy(ohlcv_data, args)

    # Backtest
    if args.backtest:
        strategy.backtest()
        exit()

    # Run strategy
    position = strategy.execute()

    # If strategy suggests a position, open it. Otherwise, don't do anything.
    if position:
        exchange.open_position(position)
    else:
        print(f'\nDid not have any opportunity to open a position')

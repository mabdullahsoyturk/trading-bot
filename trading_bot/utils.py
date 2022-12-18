import datetime
import argparse
from typing import Union

BINANCE_LOWER_LIMIT = 0.001

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--symbol', type=str, help='Ticker symbol', default='BTC/USDT')
    parser.add_argument('--timeframe', type=str, help='Timeframe', default='30m')
    parser.add_argument('--ema-timeperiod', type=int, help='Timeperiod for EMA', default=600)
    parser.add_argument('--atr-multiplier', type=float, help='ATR multiplier', default=2)
    parser.add_argument('--risk', type=float, help="Risk in dollars for 1R", default=5.0)
    parser.add_argument('--rr', type=float, help="Reward/Risk ratio", default=1.5)
    parser.add_argument('--leverage', type=int, help="Maximum leverage", default=8)
    parser.add_argument('--days-ago', type=float, help="Decides how many days worth of data we need to pull", default=20.0)

    parser.add_argument('--export', action='store_true')
    parser.add_argument('--export-path', type=str, help="Export path for positions", default="/home/soyturk")

    parser.add_argument('--backtest', action='store_true')
    parser.add_argument('--visualize', action='store_true')
    parser.add_argument('--backtest-export', action='store_true')

    return parser.parse_args()

def get_amount(budget:float, side:str, price:float, stop_loss:float, risk:float=1.0) -> Union[float, None]:
    args = get_args()
    amount = 0.0
    leverage = 1
    
    try:
        if side == 'buy':
            amount = risk / (price - stop_loss)
        elif side == 'sell':
            amount = risk / (stop_loss - price)
        else:
            print("Unknown side. Should be buy or sell")
        
        print(f'Price: {price:.2f}, Stop Loss: {stop_loss:.2f}, Amount: {amount}')
        cost = amount * price

        if cost > budget:
            leverage = int(cost // budget) + 1 

        print(f'Budget: {budget:.2f}, Amount: {amount}, Cost: {cost:.2f}, Leverage: {leverage}')

        if amount < BINANCE_LOWER_LIMIT:
            raise Exception(f'Amount ({amount}) cannot be smaller than minimum amount {BINANCE_LOWER_LIMIT}')
        if leverage > args.leverage:
            raise Exception(f'Too much leverage: {leverage}. Budget is not enough')
        
        return amount, leverage
    except Exception as e:
        print(e)
        return None, None

def get_x_days_ago_in_iso(x:float=5.0) -> str:
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=x)
    return (today - delta).isoformat()

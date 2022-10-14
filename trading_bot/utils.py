import datetime
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--symbol', type=str, help='Ticker symbol', default='BTC/USDT')
    parser.add_argument('--timeframe', type=str, help='Timeframe', default='30m')
    parser.add_argument('--ema-timeperiod', type=int, help='Timeperiod for EMA', default=200)
    parser.add_argument('--atr-multiplier', type=float, help='ATR multiplier', default=2)
    parser.add_argument('--risk', type=float, help="Risk in dollars for 1R", default=1.0)
    parser.add_argument('--rr', type=float, help="Reward/Risk ratio", default=2)
    parser.add_argument('--leverage', type=int, help="Leverage in futures", default=1)
    parser.add_argument('--days-ago', type=float, help="Decides how many days worth of data we need to pull", default=20.0)

    parser.add_argument('--export', action='store_true')
    parser.add_argument('--export-path', type=str, help="Export path for positions", default="/home/soyturk")

    parser.add_argument('--backtest', action='store_true')
    parser.add_argument('--backtest-export', action='store_true')

    return parser.parse_args()

def get_amount(budget:float, side:str, price:float, stop_loss:float, risk:float=1.0) -> float:
    amount = 0.0
    
    try:
        if side == 'buy':
            amount = risk / (price - stop_loss)
        elif side == 'sell':
            amount = risk / (stop_loss - price)
        else:
            print("Unknown side. Should be buy or sell")
        
        print(f'Budget: {budget}, Amount: {amount}, Cost: {amount * price}')

        if amount < 0.001:
            raise Exception("Smaller than minimum amount 0.001")
        if amount * price > budget:
            raise Exception("Budget is not enough")
        
        return amount
    except Exception as e:
        print(e)
        return None

def get_x_days_ago_in_iso(x:float=5.0) -> str:
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=x)
    return (today - delta).isoformat()

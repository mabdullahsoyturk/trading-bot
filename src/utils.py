import ccxt
import datetime

def get_balance(exchange):
    return exchange.fetch_balance()

def get_amount(budget, side, price, stop_loss, take_profit, risk=2.5):
    amount = (budget / price)
    
    loss_in_dollars = (price - stop_loss) * amount

    assert loss_in_dollars <= risk

    return amount

def create_order(exchange, order):
    try:
        print(f'Trying to execute: {order}')
        opened_order = exchange.create_order(order.symbol, order.type, order.side, order.amount, order.price, order.params)
        print(opened_order)
    except Exception as e:
        print(e)

def get_x_days_ago_in_iso(x=2):
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=2)
    return (today - delta).isoformat()

if __name__ == '__main__':
    print(get_amount(80, 'long', 20000, 19500, 20750))
    print(get_x_days_ago_in_iso(2))
import ccxt
import datetime

def get_balance(exchange):
    return exchange.fetch_balance()

def get_amount(budget, side, price, stop_loss, risk=2):
    amount = 0
    
    if side == 'buy':
        amount = risk / (price - stop_loss)
    elif side == 'sell':
        amount = risk / (stop_loss - price)
    else:
        print("Unknown side. Should be buy or sell")

    print(amount)

    assert amount > 0.001
    assert amount * price < budget

    return amount

def create_order(exchange, order):
    try:
        print(f'Trying to execute: {order}')
        opened_order = exchange.create_order(order.symbol, order.type, order.side, order.amount, order.price, order.params)
        print(opened_order)

        return opened_order
    except Exception as e:
        print(e)
        return None

def get_x_days_ago_in_iso(x=2):
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=2)
    return (today - delta).isoformat()

if __name__ == '__main__':
    print(get_amount(80, 'buy', 20000, 19500))
    print(get_amount(80, 'sell', 19500, 20000))
    print(get_x_days_ago_in_iso(2))
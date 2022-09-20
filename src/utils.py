import ccxt
import datetime

def get_balance(exchange):
    return exchange.fetch_balance()

def get_amount(budget, side, price, stop_loss, risk=1):
    amount = 0
    
    if side == 'buy':
        amount = risk / (price - stop_loss)
    elif side == 'sell':
        amount = risk / (stop_loss - price)
    else:
        print("Unknown side. Should be buy or sell")

    assert(amount > 0.001, "Smaller than minimum amount 0.001")
    assert(amount * price < budget, "Budget is not enough")

    print(amount)

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

def get_x_days_ago_in_iso(x=5):
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=x)
    return (today - delta).isoformat()

if __name__ == '__main__':
    #print(get_amount(80, 'buy', 20000, 19500))
    print(get_amount(175, 'sell', 19702.4, 19742.5))
    #print(get_x_days_ago_in_iso(2))

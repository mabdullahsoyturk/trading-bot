from dataclasses import dataclass
from typing import Union

@dataclass
class Order:
    symbol: str                     # BTC/USDT or ETH/USDT
    type: str                       # limit or market
    side: str                       # sell or buy
    amount: float                   # amount of the product, e.g. 0.01 BTC 
    price: Union[float, None]       # price 
    params: dict                    # params = {'test': True, 'stop_price': 0.01} or params = {'test': False, 'stop_price': 0.01}
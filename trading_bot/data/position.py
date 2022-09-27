from dataclasses import dataclass
from datetime import datetime
from typing import Union

@dataclass
class Position:
    side: str                       # buy or sell
    opening_time: datetime          # open time
    entry_price: float              # entry price
    stop_loss: float                # stop loss price
    take_profit: float              # take profit price
    rr: float = 0                     # reward/risk ratio
    closing_time: Union[datetime, None] = None   # close time

    def __repr__(self):
        return [self.side, self.opening_time, self.entry_price, self.stop_loss, self.take_profit, self.rr, self.closing_time]
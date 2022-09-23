from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    side: str               # buy or sell
    opening_time: datetime  # open time
    entry_price: float      # entry price
    stop_loss: float        # stop loss price
    take_profit: float      # take profit price
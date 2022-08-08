from dataclasses import dataclass

@dataclass
class OHLCV:
    timestamp: int
    open_price: float
    highest: float
    lowest: float
    close_price: float
    volume: float
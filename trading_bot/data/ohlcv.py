from dataclasses import dataclass

@dataclass
class OHLCV:
    """
        O = Open
        H = High
        L = Low
        C = Close
        V = Volume
    """
    timestamp: int      # Timestamp
    open_price: float   # Opening price of the candle
    highest: float      # Highest price of the candle
    lowest: float       # Lowest price of the candle
    close_price: float  # Closing price of the candle
    volume: float       # Volume
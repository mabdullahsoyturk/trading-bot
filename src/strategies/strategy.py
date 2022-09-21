from abc import ABC, abstractmethod

import talib

class Strategy(ABC):
    """
        Abstract strategy class to be extended by each specific strategy.
        Required methods to be implemented:
        
        - execute() -> Executes both long and short strategies
        - long() -> Long strategy
        - short() -> Short strategy
    """
    
    def __init__(self, ohlcvs, ohlcv_data, rr=2):
        self.ohlcvs = ohlcvs
        self.ohlcv_data = ohlcv_data
        self.highs = ohlcv_data[:, 2]
        self.lows = ohlcv_data[:, 3]
        self.closes = ohlcv_data[:, 4]
        self.rr = rr

    def get_last_three_candles(self):
        return self.ohlcvs[0], self.ohlcvs[1], self.ohlcvs[2]

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def long(self):
        pass

    @abstractmethod
    def short(self):
        pass
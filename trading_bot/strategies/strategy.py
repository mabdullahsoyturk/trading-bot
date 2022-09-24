from abc import ABC, abstractmethod

import numpy as np
import talib

class Strategy(ABC):
    """
        Abstract strategy class to be extended by each specific strategy.
        Required methods to be implemented:
        
        - execute() -> Executes both long and short strategies
        - long() -> Long strategy
        - short() -> Short strategy
    """
    
    def __init__(self, ohlcv_data, rr=2):
        self.ohlcv_data = np.array(ohlcv_data)
        self.highs = self.ohlcv_data[:, 2]
        self.lows = self.ohlcv_data[:, 3]
        self.closes = self.ohlcv_data[:, 4]
        self.rr = rr

    def backtest(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def long(self):
        pass

    @abstractmethod
    def short(self):
        pass
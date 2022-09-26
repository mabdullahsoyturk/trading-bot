from abc import ABC, abstractmethod
from typing import Union, Optional

import numpy as np
import talib

from trading_bot.data import Position

class Strategy(ABC):
    """
        Abstract strategy class to be extended by each specific strategy.
        Required methods to be implemented:
        
        - execute() -> Executes both long and short strategies
        - long() -> Long strategy
        - short() -> Short strategy
    """
    
    def __init__(self, ohlcv_data:list, rr:Optional[float]=2.0):
        self.ohlcv_data = np.array(ohlcv_data)
        self.highs = self.ohlcv_data[:, 2]
        self.lows = self.ohlcv_data[:, 3]
        self.closes = self.ohlcv_data[:, 4]
        self.rr = rr

    def backtest(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> Union[Position, None]:
        pass

    @abstractmethod
    def long(self) -> Union[Position, None]:
        pass

    @abstractmethod
    def short(self) -> Union[Position, None]:
        pass
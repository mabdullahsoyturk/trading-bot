import datetime
import talib # type: ignore

from trading_bot.data import OHLCV, Position
from trading_bot.strategies.strategy import Strategy
from trading_bot.backtest import Summary

from typing import Union

class EngulfingStrategy(Strategy):
    """
        Checks last 3 candles. Open position if:

        a. 1 up engulf after 2 down in an uptrend (above 200 EMA)
        b. 1 down engulf after 2 up in a downtrend (below 200 EMA)

        Avoids fluctuations with ATR. If last candle moves more than 2 ATR, do not enter.  

        rr = Reward/Risk Ratio
    """
    def __init__(self, ohlcv_data, args):
        super().__init__(ohlcv_data, rr=args.rr)
        self.timeperiod = args.ema_timeperiod
        self.atr_multiplier = args.atr_multiplier
        self.ema = talib.EMA(self.closes, timeperiod=self.timeperiod)
        self.atr = talib.ATR(self.highs, self.lows, self.closes)

    def get_three_candles(self, index:int=-2) -> tuple[OHLCV, OHLCV, OHLCV]:
        return self.ohlcvs[index - 2], self.ohlcvs[index - 1], self.ohlcvs[index]

    def execute(self) -> Union[Position, None]:
        long_position = self.long()
        short_position = self.short()

        if long_position:
            return long_position

        if short_position:
            return short_position
        
        return None

    def long(self, index:int=-2) -> Union[Position, None]:
        first_candle, second_candle, engulf_candle = self.get_three_candles(index)
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        # print(f'\n[LONG, {open_time}] First Candle Check: {first_candle.close_price < first_candle.open_price}')
        # print(f'[LONG, {open_time}] Second Candle Check: {second_candle.close_price < second_candle.open_price}')
        # print(f'[LONG, {open_time}] Engulf Check: {engulf_candle.close_price > second_candle.open_price}')
        # print(f'[LONG, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[index] * self.atr_multiplier}')
        # print(f'[LONG, {open_time}] EMA: {self.ema[index] < engulf_candle.close_price}')

        if first_candle.close_price < first_candle.open_price and \
                second_candle.close_price < second_candle.open_price and \
                engulf_candle.close_price > second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[index] * self.atr_multiplier and \
                self.ema[index] < engulf_candle.close_price:
            
            entry_price = engulf_candle.close_price
            whichever_is_lowest = second_candle.lowest if second_candle.highest < engulf_candle.highest else engulf_candle.lowest
            stop_loss = whichever_is_lowest
            take_profit = entry_price + (entry_price - stop_loss) * self.rr

            print(f'\n[LONG][{open_time}] Opened at: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}, EMA: {self.ema[index]:.2f} ATR: {self.atr[index]:.2f}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit)
            
            return position

        return None

    def short(self, index:int=-2) -> Union[Position, None]:
        first_candle, second_candle, engulf_candle = self.get_three_candles(index)
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        # print(f'\n[SHORT, {open_time}] First Candle Check: {first_candle.close_price > first_candle.open_price}')
        # print(f'[SHORT, {open_time}] Second Candle Check: {second_candle.close_price > second_candle.open_price}')
        # print(f'[SHORT, {open_time}] Engulf Check: {engulf_candle.close_price < second_candle.open_price}')
        # print(f'[SHORT, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[index] * self.atr_multiplier}')
        # print(f'[SHORT, {open_time}] EMA: {self.ema[index] > engulf_candle.close_price}')

        if first_candle.close_price > first_candle.open_price and \
                second_candle.close_price > second_candle.open_price and \
                engulf_candle.close_price < second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[index] * self.atr_multiplier and \
                self.ema[index] > engulf_candle.close_price:

            entry_price = engulf_candle.close_price
            whichever_is_highest = second_candle.highest if second_candle.highest > engulf_candle.highest else engulf_candle.highest
            stop_loss = whichever_is_highest
            take_profit = entry_price - (stop_loss - entry_price) * self.rr

            print(f'\n[SHORT][{open_time}] Opened at: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}, EMA: {self.ema[index]:.2f} ATR: {self.atr[index]:.2f}')

            position = Position("sell", open_time, entry_price, stop_loss, take_profit)

            return position

        return None
        
import numpy as np
import talib
import datetime

from src.data import OHLCV, Position
from src.strategies.strategy import Strategy

timeperiod = 200
atr_multiplier = 1.5

class MacdStrategy(Strategy):
    def __init__(self, ohlcv_data, timeperiod=200, atr_multiplier=2):
        super().__init__(ohlcv_data, rr=1.5)
        self.timeperiod = timeperiod
        self.atr_multiplier = atr_multiplier
        self.ohlcvs = [OHLCV(*data) for data in self.ohlcv_data]
        self.ema = talib.EMA(self.closes, timeperiod=timeperiod)
        self.atr = talib.ATR(self.highs, self.lows, self.closes)
        self.macd, self.signal, _ = talib.MACD(self.closes)

    def execute(self):
        long_position = self.long()
        short_position = self.short()

        if long_position:
            return long_position

        if short_position:
            return short_position

    def get_last_three_candles(self):
        return self.ohlcvs[-4], self.ohlcvs[-3], self.ohlcvs[-2]

    def long(self):
        first_candle, second_candle, third_candle = self.get_last_three_candles()
        open_time = datetime.datetime.fromtimestamp(third_candle.timestamp/1000.0)

        print(f'[LONG, {open_time}] EMA Check: {self.ema[-2] < third_candle.close_price}')
        print(f'[LONG, {open_time}] MACD Check: {self.macd[-2] < 0}')
        print(f'[LONG, {open_time}] MACD Crossover: {self.macd[-2] > self.signal[-2] and self.macd[-3] < self.signal[-3]}')

        if third_candle.close_price > self.ema[-2] and \
            self.macd[-2] < 0 and \
            self.macd[-2] > self.signal[-2] and self.macd[-3] < self.signal[-3]:
            
            entry_price = third_candle.close_price

            stop_loss = 0

            prev_low = reversed(self.ohlcvs[:-2])[0].lowest
            for ohlcv in reversed(self.ohlcvs[:-2]):
                if ohlcv.lowest < prev_low:
                    prev_low = ohlcv.lowest
                else:
                    break

            stop_loss = prev_low
            take_profit = entry_price + (entry_price - stop_loss) * self.rr

            print(f'\n[LONG][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} MACD: {self.macd[-2]}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit)
            
            return position

    def short(self):
        first_candle, second_candle, third_candle = self.get_last_three_candles()
        open_time = datetime.datetime.fromtimestamp(third_candle.timestamp/1000.0)

        print(f'[SHORT, {open_time}] EMA Check: {self.ema[-2] > third_candle.close_price}')
        print(f'[SHORT, {open_time}] MACD Check: {self.macd[-2] > 0}')
        print(f'[SHORT, {open_time}] MACD Crossover: {self.macd[-2] < self.signal[-2] and self.macd[-3] > self.signal[-3]}')

        if self.ema[-2] > third_candle.close_price and \
            self.macd[-2] > 0 and \
            self.macd[-2] < self.signal[-2] and self.macd[-3] > self.signal[-3]:
            
            entry_price = third_candle.close_price

            stop_loss = 0

            prev_high = reversed(self.ohlcvs[:-2])[0].highest
            for ohlcv in reversed(self.ohlcvs[:-2]):
                if ohlcv.highest > prev_high:
                    prev_high = ohlcv.highest
                else:
                    break

            stop_loss = prev_high
            take_profit = entry_price - (stop_loss - entry_price) * self.rr

            print(f'\n[SHORT][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} MACD: {self.macd[-2]}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit)
            
            return position
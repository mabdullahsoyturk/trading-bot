import numpy as np
import talib
import datetime
from src.position import Position

timeperiod = 200
rr = 2
atr_multiplier = 2

class EngulfingStrategy():
    def __init__(self, ohlcvs, ohlcv_data):
        self.ohlcvs = ohlcvs
        self.ohlcv_data = ohlcv_data
        self.highs = ohlcv_data[:, 2]
        self.lows = ohlcv_data[:, 3]
        self.closes = ohlcv_data[:, 4]
        self.ema = talib.EMA(self.closes, timeperiod=timeperiod)
        self.atr = talib.ATR(self.highs, self.lows, self.closes)

    def execute(self):
        long_position = self.two_to_one_engulf_long()
        short_position = self.two_to_one_engulf_short()

        if long_position:
            return long_position

        if short_position:
            return short_position

    def get_last_three_candles(self):
        return self.ohlcvs[0], self.ohlcvs[1], self.ohlcvs[2]

    def two_to_one_engulf_long(self):
        first_candle, second_candle, engulf_candle = self.get_last_three_candles()
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'\n[LONG, {open_time}] First Candle Check: {first_candle.close_price < first_candle.open_price}')
        print(f'[LONG, {open_time}] Second Candle Check: {second_candle.close_price < second_candle.open_price}')
        print(f'[LONG, {open_time}] Engulf Check: {engulf_candle.close_price > second_candle.open_price}')
        print(f'[LONG, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * atr_multiplier}')
        print(f'[LONG, {open_time}] EMA Check: {self.ema[-2] < engulf_candle.close_price}')

        if first_candle.close_price < first_candle.open_price and \
                second_candle.close_price < second_candle.open_price and \
                engulf_candle.close_price > second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * atr_multiplier and \
                self.ema[-2] < engulf_candle.close_price:
            
            entry_price = engulf_candle.close_price
            whichever_is_lowest = second_candle.lowest if second_candle.highest < engulf_candle.highest else engulf_candle.lowest
            stop_loss = whichever_is_lowest
            take_profit = entry_price + (entry_price - stop_loss) * rr

            print(f'\n[LONG][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} ATR: {self.atr[-2]}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit, self.ema[-2], self.atr[-2])
            
            return position

    def two_to_one_engulf_short(self):
        first_candle, second_candle, engulf_candle = self.get_last_three_candles()
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'\n[SHORT, {open_time}] First Candle Check: {first_candle.close_price > first_candle.open_price}')
        print(f'[SHORT, {open_time}] Second Candle Check: {second_candle.close_price > second_candle.open_price}')
        print(f'[SHORT, {open_time}] Engulf Check: {engulf_candle.close_price < second_candle.open_price}')
        print(f'[SHORT, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * atr_multiplier}')
        print(f'[SHORT, {open_time}] EMA Check: {self.ema[-2] > engulf_candle.close_price}')

        if first_candle.close_price > first_candle.open_price and \
                second_candle.close_price > second_candle.open_price and \
                engulf_candle.close_price < second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * atr_multiplier and \
                self.ema[-2] > engulf_candle.close_price:

            entry_price = engulf_candle.close_price
            whichever_is_highest = second_candle.highest if second_candle.highest > engulf_candle.highest else engulf_candle.highest
            stop_loss = whichever_is_highest
            take_profit = entry_price - (stop_loss - entry_price) * rr

            print(f'\n[SHORT][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} ATR: {self.atr[-2]}')

            position = Position("sell", open_time, entry_price, stop_loss, take_profit, self.ema[-2], self.atr[-2])

            return position

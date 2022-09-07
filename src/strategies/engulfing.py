import numpy as np
import talib
import datetime
from src.position import Position

timeperiod = 50
rr = 1.5
atr_multiplier = 1.5

class EngulfingStrategy():
    def __init__(self, ohlcvs, ohlcv_data):
        self.ohlcvs = ohlcvs
        self.ohlcv_data = ohlcv_data

    def execute(self):
        long_position = self.two_to_one_engulf_long()
        short_position = self.two_to_one_engulf_short()

        if long_position:
            return long_position

        if short_position:
            return short_position

    def two_to_one_engulf_long(self):
        r = 0

        num_stops = 0
        num_take_profits = 0
        num_positions = 0

        highs = np.array([element[2] for element in self.ohlcv_data])
        lows = np.array([element[3] for element in self.ohlcv_data])
        closes = np.array([element[4] for element in self.ohlcv_data])
        ema = talib.EMA(closes, timeperiod=timeperiod)
        atr = talib.ATR(highs, lows, closes)

        first_candle = self.ohlcvs[0]
        second_candle = self.ohlcvs[1]
        engulf_candle = self.ohlcvs[2]
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'[LONG, {open_time}] First Candle Check: {first_candle.close_price < first_candle.open_price}')
        print(f'[LONG, {open_time}] Second Candle Check: {second_candle.close_price < second_candle.open_price}')
        print(f'[LONG, {open_time}] Engulf Check: {engulf_candle.close_price > second_candle.open_price}')
        print(f'[LONG, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < atr[-2] * atr_multiplier}')
        print(f'[LONG, {open_time}] EMA Check: {ema[-2] < engulf_candle.close_price}')

        if first_candle.close_price < first_candle.open_price and \
                second_candle.close_price < second_candle.open_price and \
                engulf_candle.close_price > second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < atr[-2] * atr_multiplier and \
                ema[-2] < engulf_candle.close_price:
            num_positions += 1

            entry_price = engulf_candle.close_price
            whichever_is_lowest = second_candle.lowest if second_candle.highest < engulf_candle.highest else engulf_candle.lowest
            stop_loss = whichever_is_lowest
            take_profit = entry_price + (entry_price - stop_loss) * rr

            print(f'\n[LONG][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {ema[-2]} ATR: {atr[-2]}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit, ema[-2], atr[-2])
            
            return position

    def two_to_one_engulf_short(self):
        r = 0
        num_stops = 0
        num_take_profits = 0
        num_positions = 0

        highs = np.array([element[2] for element in self.ohlcv_data])
        lows = np.array([element[3] for element in self.ohlcv_data])
        closes = np.array([element[4] for element in self.ohlcv_data])

        ema = talib.EMA(closes, timeperiod=timeperiod)
        atr = talib.ATR(highs, lows, closes)

        first_candle = self.ohlcvs[0]
        second_candle = self.ohlcvs[1]
        engulf_candle = self.ohlcvs[2]
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'[SHORT, {open_time}] First Candle Check: {first_candle.close_price < first_candle.open_price}')
        print(f'[SHORT, {open_time}] Second Candle Check: {second_candle.close_price < second_candle.open_price}')
        print(f'[SHORT, {open_time}] Engulf Check: {engulf_candle.close_price > second_candle.open_price}')
        print(f'[SHORT, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < atr[-2] * atr_multiplier}')
        print(f'[SHORT, {open_time}] EMA Check: {ema[-2] < engulf_candle.close_price}')

        if first_candle.close_price > first_candle.open_price and \
                second_candle.close_price > second_candle.open_price and \
                engulf_candle.close_price < second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < atr[-2] * atr_multiplier and \
                ema[-2] > engulf_candle.close_price:
            num_positions += 1

            entry_price = engulf_candle.close_price
            whichever_is_highest = second_candle.highest if second_candle.highest > engulf_candle.highest else engulf_candle.highest
            stop_loss = whichever_is_highest
            take_profit = entry_price - (stop_loss - entry_price) * rr

            print(f'\n[SHORT][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {ema[-2]} ATR: {atr[-2]}')

            position = Position("sell", open_time, entry_price, stop_loss, take_profit, ema[-2], atr[-2])

            return position

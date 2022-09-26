import datetime
import talib

from trading_bot.data import OHLCV, Position
from trading_bot.strategies.strategy import Strategy
from trading_bot.backtest import Summary

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
        self.ohlcvs = [OHLCV(*data) for data in self.ohlcv_data]
        self.ema = talib.EMA(self.closes, timeperiod=self.timeperiod)
        self.atr = talib.ATR(self.highs, self.lows, self.closes)

    def get_last_three_candles(self):
        return self.ohlcvs[-4], self.ohlcvs[-3], self.ohlcvs[-2]

    def execute(self):
        first_candle, second_candle, engulf_candle = self.get_last_three_candles()
        long_position = self.long(first_candle, second_candle, engulf_candle)
        short_position = self.short(first_candle, second_candle, engulf_candle)

        if long_position:
            return long_position

        if short_position:
            return short_position

    def long(self, first_candle, second_candle, engulf_candle):
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'\n[LONG, {open_time}] First Candle Check: {first_candle.close_price < first_candle.open_price}')
        print(f'[LONG, {open_time}] Second Candle Check: {second_candle.close_price < second_candle.open_price}')
        print(f'[LONG, {open_time}] Engulf Check: {engulf_candle.close_price > second_candle.open_price}')
        print(f'[LONG, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * self.atr_multiplier}')
        print(f'[LONG, {open_time}] EMA: {self.ema[-2]}, Close: {engulf_candle.close_price}')

        if first_candle.close_price < first_candle.open_price and \
                second_candle.close_price < second_candle.open_price and \
                engulf_candle.close_price > second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * self.atr_multiplier and \
                self.ema[-2] < engulf_candle.close_price:
            
            entry_price = engulf_candle.close_price
            whichever_is_lowest = second_candle.lowest if second_candle.highest < engulf_candle.highest else engulf_candle.lowest
            stop_loss = whichever_is_lowest
            take_profit = entry_price + (entry_price - stop_loss) * self.rr

            print(f'\n[LONG][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} ATR: {self.atr[-2]}')
            position = Position("buy", open_time, entry_price, stop_loss, take_profit)
            
            return position

    def short(self, first_candle, second_candle, engulf_candle):
        open_time = datetime.datetime.fromtimestamp(engulf_candle.timestamp/1000.0)

        print(f'\n[SHORT, {open_time}] First Candle Check: {first_candle.close_price > first_candle.open_price}')
        print(f'[SHORT, {open_time}] Second Candle Check: {second_candle.close_price > second_candle.open_price}')
        print(f'[SHORT, {open_time}] Engulf Check: {engulf_candle.close_price < second_candle.open_price}')
        print(f'[SHORT, {open_time}] ATR Check: {engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * self.atr_multiplier}')
        print(f'[SHORT, {open_time}] EMA: {self.ema[-2]}, Close: {engulf_candle.close_price}')

        if first_candle.close_price > first_candle.open_price and \
                second_candle.close_price > second_candle.open_price and \
                engulf_candle.close_price < second_candle.open_price and \
                engulf_candle.highest - engulf_candle.lowest < self.atr[-2] * self.atr_multiplier and \
                self.ema[-2] > engulf_candle.close_price:

            entry_price = engulf_candle.close_price
            whichever_is_highest = second_candle.highest if second_candle.highest > engulf_candle.highest else engulf_candle.highest
            stop_loss = whichever_is_highest
            take_profit = entry_price - (stop_loss - entry_price) * self.rr

            print(f'\n[SHORT][{open_time}] Opened at: {entry_price}, Stop Loss: {stop_loss}, Take Profit: {take_profit}, EMA: {self.ema[-2]} ATR: {self.atr[-2]}')

            position = Position("sell", open_time, entry_price, stop_loss, take_profit)

            return position

    def backtest_long(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            first_candle = self.ohlcvs[index - 2]
            second_candle = self.ohlcvs[index - 1]
            engulf_candle = self.ohlcvs[index]

            position = self.long(first_candle, second_candle, engulf_candle)

            if position:
                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

                    if candle.highest > position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.rr
                        position.closing_time = closing_time
                        break

                    if candle.lowest <= position.stop_loss:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Stop loss')
                        position.rr = -1
                        position.closing_time = closing_time
                        break

                positions.append(position)

        return positions

    def backtest_short(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            first_candle = self.ohlcvs[index - 2]
            second_candle = self.ohlcvs[index - 1]
            engulf_candle = self.ohlcvs[index]

            position = self.short(first_candle, second_candle, engulf_candle)

            if position:
                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

                    if candle.lowest < position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.rr
                        position.closing_time = closing_time
                        break

                    if candle.highest >= position.stop_loss:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Stop loss')
                        position.rr = -1
                        position.closing_time = closing_time
                        break

                positions.append(position)

        return positions

    def backtest(self):
        long_positions = self.backtest_long()
        short_positions = self.backtest_short()
        
        summary = Summary(self.rr, long_positions, short_positions)
        summary.print()
        
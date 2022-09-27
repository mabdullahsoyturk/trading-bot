import datetime
from trading_bot.backtest import Summary

class Backtester:
    def __init__(self, strategy):
        self.strategy = strategy

    def __call__(self, ohlcvs):
        long_positions = self.backtest_long(ohlcvs)
        short_positions = self.backtest_short(ohlcvs)
        
        summary = Summary(self.strategy.rr, long_positions, short_positions)
        summary.print()

    def backtest_long(self, ohlcvs):
        positions = []

        for index in range(2, len(ohlcvs)):
            first_candle = ohlcvs[index - 2]
            second_candle = ohlcvs[index - 1]
            engulf_candle = ohlcvs[index]

            position = self.strategy.long(first_candle, second_candle, engulf_candle, index)

            if position:
                for runner_index in range(index + 1, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.highest > position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.strategy.rr
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

    def backtest_short(self, ohlcvs):
        positions = []

        for index in range(2, len(ohlcvs)):
            first_candle = ohlcvs[index - 2]
            second_candle = ohlcvs[index - 1]
            engulf_candle = ohlcvs[index]

            position = self.strategy.short(first_candle, second_candle, engulf_candle, index)

            if position:
                for runner_index in range(index + 1, len(ohlcvs)):
                    candle = ohlcvs[runner_index]

                    if candle.lowest < position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.strategy.rr
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
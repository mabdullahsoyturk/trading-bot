import datetime
import csv

from trading_bot.backtest import Summary

class Backtester:
    def __init__(self, strategy, args):
        self.strategy = strategy
        self.ohlcvs = strategy.ohlcvs
        self.args = args

    def __call__(self):
        long_positions = self.backtest_long()
        short_positions = self.backtest_short()
        
        summary = Summary(self.strategy.rr, long_positions, short_positions)
        summary.print()

        if self.args.backtest_export:
            with open(self.args.export_path + "/backtest_positions.csv", 'w') as export_file:
                csv_writer = csv.writer(export_file, delimiter=',')

                for position in long_positions + short_positions:
                    csv_writer.writerow(position.__repr__())

    def backtest_long(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            position = self.strategy.long(index)

            if position:
                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

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

    def backtest_short(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            position = self.strategy.short(index)

            if position:
                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

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
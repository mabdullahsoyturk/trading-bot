import datetime
import csv

from trading_bot.backtest import Summary
from trading_bot.utils import get_amount

class Backtester:
    def __init__(self, strategy, args, balance):
        self.strategy = strategy
        self.ohlcvs = strategy.ohlcvs
        self.args = args
        self.balance = balance
        self.balance = 1000

    def __call__(self):
        long_positions = self.backtest_long()
        short_positions = self.backtest_short()
        
        summary = Summary(self.strategy.rr, long_positions, short_positions)
        summary.print()
        if self.args.visualize:
            summary.visualize()

        print(f'Final balance: {self.balance}')

        if self.args.backtest_export:
            with open(self.args.export_path + "/backtest_positions.csv", 'w') as export_file:
                csv_writer = csv.writer(export_file, delimiter=',')

                for position in long_positions + short_positions:
                    csv_writer.writerow(position.__repr__())

    def get_cost(self, position, amount):
        if amount:
            return amount * position.entry_price

        return None

    def backtest_long(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            position = self.strategy.long(index)

            if position:
                amount, leverage = get_amount(self.balance, position.side, position.entry_price, position.stop_loss, risk=self.args.risk)
                cost = self.get_cost(position, amount)
                if cost:
                    print(f'[{position.opening_time}] --> Cost: {cost}$')
                else:
                    continue

                self.balance -= cost

                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

                    if candle.highest > position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.strategy.rr
                        position.closing_time = closing_time
                        self.balance += cost + (position.take_profit - position.entry_price) * amount
                        break

                    if candle.lowest <= position.stop_loss:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Stop loss')
                        position.rr = -1
                        position.closing_time = closing_time
                        self.balance +=  cost - (position.entry_price - position.stop_loss) * amount
                        break
                
                if position.closing_time:
                    positions.append(position)
                else:
                    self.balance += cost

        return positions

    def backtest_short(self):
        positions = []

        for index in range(2, len(self.ohlcvs)):
            position = self.strategy.short(index)

            if position:
                amount, leverage = get_amount(self.balance, position.side, position.entry_price, position.stop_loss, risk=self.args.risk)
                cost = self.get_cost(position, amount)
                if cost:
                    print(f'[{position.opening_time}] --> Cost: {cost}$')
                else:
                    continue

                self.balance -= cost

                for runner_index in range(index + 1, len(self.ohlcvs)):
                    candle = self.ohlcvs[runner_index]

                    if candle.lowest < position.take_profit:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Take profit')
                        position.rr = self.strategy.rr
                        position.closing_time = closing_time
                        self.balance += cost + (position.entry_price - position.take_profit) * amount
                        break

                    if candle.highest >= position.stop_loss:
                        closing_time = datetime.datetime.fromtimestamp(candle.timestamp/1000.0)
                        print(f'[{closing_time}] Stop loss')
                        position.rr = -1
                        position.closing_time = closing_time
                        self.balance += cost - (position.stop_loss - position.entry_price) * amount
                        break
                
                if position.closing_time:
                    positions.append(position)
                else:
                    self.balance += cost

        return positions
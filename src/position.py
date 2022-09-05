class Position:
    def __init__(self, side, opening_time, entry_price, stop_loss, take_profit, ema, atr):
        self.side = side
        self.opening_time = opening_time
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.ema = ema
        self.atr = atr
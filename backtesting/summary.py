import numpy as np
import matplotlib.pyplot as plt

class Summary:
    def __init__(self, side):
        self.side = side
        self.r_history = []

    def visualize(self):
        r_cumsum = np.cumsum(np.array(self.r_history))

        xpoints = np.arange(1, r_cumsum.size + 1, 1, dtype=int)
        ypoints = np.array(r_cumsum)

        plt.plot(xpoints, ypoints)
        plt.show()

    def __str__(self):
        r = sum(self.r_history)
        num_stops = sum([value == -1 for value in self.r_history])
        num_take_profits = sum([value > 0 for value in self.r_history])
        num_positions = len(self.r_history)

        header = "{:.7}\t {:.2}\t\t {:.3}\t\t {:<10}\t {:<10}\t {:<10}".format('Side','R','Win Rate','Num Stops', 'Num Profits', 'Num Positions')
        entry = "{:.7}\t {:.2f}\t\t {:.3f}\t\t {:<10}\t {:<10}\t {:<10}".format(self.side, r, num_take_profits / num_positions, num_stops, num_take_profits, num_positions)
        return "\n".join([header, entry])
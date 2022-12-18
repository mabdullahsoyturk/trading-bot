import collections
import numpy as np
import matplotlib.pyplot as plt # type: ignore

from trading_bot.data import Position

class Summary:
    def __init__(self, rr:float, long_positions:list[Position], short_positions:list[Position]):
        self.rr = rr
        self.long_positions = long_positions
        self.short_positions = short_positions

    def get_r_history(self, positions:list[Position]) -> list[float]:
        """Returns r history of positions

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            list[float]: List of floats containing -1 or rr
        """
        return [position.rr for position in positions]

    def get_durations(self, positions:list[Position]) -> list[float]:
        """Returns durations of the positions in hours

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            list[float]: List of durations in hours
        """
        return [(position.closing_time - position.opening_time).total_seconds() / 3600 for position in positions if position.closing_time]

    def get_number_of_stops(self, positions:list[Position]) -> int:
        """Number of stop loss positions

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            int: Number of positions which hit the stop loss level
        """
        num_stops = 0

        for position in positions:
            if position.rr == -1:
                num_stops += 1

        return num_stops

    def get_number_of_profits(self, positions:list[Position]) -> int:
        """Number of take profit positions

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            int: Number of positions which hit the take profit level
        """
        num_profits = 0

        for position in positions:
            if position.rr > 0:
                num_profits += 1

        return num_profits

    def get_win_rate(self, positions:list[Position]) -> float:
        """Calculates win rate of closed positions

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            float: Win rate
        """
        num_profits = self.get_number_of_profits(positions)
        num_positions = num_profits + self.get_number_of_stops(positions)
        return num_profits / num_positions if num_positions != 0 else 0

    def get_longest_streak(self, positions:list[Position]) -> tuple[int, int]:
        """Number of longest consecutive wins and loses

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            tuple[int, int]: Longest consecutive wins and loses
        """
        win_streak_element = self.rr
        lose_streak_element = -1

        longest_win_streak = 0
        current_win_streak = 0

        longest_lose_streak = 0
        current_lose_streak = 0

        for position in positions:
            if position.rr == win_streak_element:
                current_win_streak += 1
            else:
                current_win_streak = 0

            if current_win_streak > longest_win_streak:
                longest_win_streak = current_win_streak

            if position.rr == lose_streak_element:
                current_lose_streak += 1
            else:
                current_lose_streak = 0

            if current_lose_streak > longest_lose_streak:
                longest_lose_streak = current_lose_streak

        return longest_win_streak, longest_lose_streak

    def get_day_stats(self, positions: list[Position]) -> tuple[int, float, int]:
        """Calculates best day, mean and worst day

        Args:
            positions (list[Position]): List of Position objects

        Returns:
            tuple[int, float, int]: (best_day, mean, worst_day)
        """
        closes = set([position.closing_time.date() for position in positions])

        # Sort by date
        date_dict = dict.fromkeys(closes, 0)
        sorted_date_dict = collections.OrderedDict(sorted(date_dict.items()))

        for position in sorted(positions):
            sorted_date_dict[position.closing_time.date()] += position.rr
        
        best_day = max(sorted_date_dict, key=sorted_date_dict.get)
        mean = sum(sorted_date_dict.values()) / len(sorted_date_dict.values())
        worst_day = min(sorted_date_dict, key=sorted_date_dict.get)
        
        return best_day, sorted_date_dict[best_day], mean, worst_day, sorted_date_dict[worst_day]

    def print(self) -> None:
        # R history
        long_r_history = self.get_r_history(self.long_positions)
        short_r_history = self.get_r_history(self.short_positions)

        # Total R
        total_long_r = sum(long_r_history)
        total_short_r = sum(short_r_history)

        # Win Rate
        long_win_rate = self.get_win_rate(self.long_positions)
        short_win_rate = self.get_win_rate(self.short_positions)

        # Num Stops
        long_num_stops = self.get_number_of_stops(self.long_positions)
        short_num_stops = self.get_number_of_stops(self.short_positions)

        # Num Profits
        long_num_profits = self.get_number_of_profits(self.long_positions)
        short_num_profits = self.get_number_of_profits(self.short_positions)

        # Durations
        long_durations = self.get_durations(self.long_positions)
        short_durations = self.get_durations(self.short_positions)

        header = "\n{:.7}\t {:.2}\t\t {:.3}\t\t {:<10}\t {:<10}\t {:<10}".format('Side','R','Win Rate','Num Stops', 'Num Profits', 'Num Positions')
        long_entry = "{:.7}\t {:.2f}\t\t {:.3f}\t\t {:<10}\t {:<10}\t {:<10}".format("LONG", total_long_r, long_win_rate, long_num_stops, long_num_profits, len(self.long_positions))
        short_entry = "{:.7}\t {:.2f}\t\t {:.3f}\t\t {:<10}\t {:<10}\t {:<10}".format("SHORT", total_short_r, short_win_rate, short_num_stops, short_num_profits, len(self.short_positions))
        general_info = "\n".join([header, long_entry, short_entry])

        print(general_info)

        # Longest streak
        long_win_streak, long_lose_streak = self.get_longest_streak(self.long_positions)
        short_win_streak, short_lose_streak = self.get_longest_streak(self.short_positions)

        header = "\n{}\t {}\t {}".format('Side', 'Longest Win Streak', 'Longest Lose Streak')
        long_entry = "{}\t\t {}\t\t\t {}".format("LONG", long_win_streak, long_lose_streak)
        short_entry = "{}\t\t {}\t\t\t {}".format("SHORT", short_win_streak, short_lose_streak)

        streak_info = "\n".join([header, long_entry, short_entry])
        print(streak_info)

        # Statistics
        long_best_day, long_best_day_rr, long_mean, long_worst_day, long_worst_day_rr = self.get_day_stats(self.long_positions)
        short_best_day, short_best_day_rr, short_mean, short_worst_day, short_worst_day_rr = self.get_day_stats(self.short_positions)

        header = "\n{}\t {}\t {}\t {}\t {}\t {}".format('Side', 'Best Day' ,'RR', 'Mean', 'Worst Day', 'RR')
        long_entry = "{}\t {}\t {}\t {:.1f}\t {}\t {}".format("LONG", long_best_day, long_best_day_rr, long_mean, long_worst_day, long_worst_day_rr)
        short_entry = "{}\t {}\t {}\t {:.1f}\t {}\t {}".format("SHORT", short_best_day, short_best_day_rr, short_mean, short_worst_day, short_worst_day_rr)

        stat_info = "\n".join([header, long_entry, short_entry])
        print(stat_info)

    def visualize(self):
        positions = self.long_positions + self.short_positions

        closes = set([position.closing_time.date() for position in positions if position.closing_time != None])

        date_dict = dict.fromkeys(closes, 0)
        sorted_date_dict = collections.OrderedDict(sorted(date_dict.items()))

        cumsum = 0

        for position in sorted(positions):
            cumsum += position.rr
            sorted_date_dict[position.closing_time.date()] = cumsum

        keys = sorted_date_dict.keys()
        values = sorted_date_dict.values()

        plt.yticks(np.arange(min(values), max(values)+1, 10))

        plt.plot(keys, values)
        plt.xlabel("Dates")
        plt.xticks(rotation=90)
        plt.ylabel("RR")
        plt.title("Cumulative Reward/Risk (RR)")
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()
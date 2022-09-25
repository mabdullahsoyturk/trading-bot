class Summary:
    def __init__(self, rr, long_positions, short_positions):
        self.rr = rr
        self.long_positions = long_positions
        self.short_positions = short_positions

    def get_r_history(self, positions):
        """ Returns r history of positions """
        return [position.rr for position in positions]

    def get_durations(self, positions):
        """ Returns durations of the positions in hours """
        return [(position.closing_time - position.opening_time).total_seconds() / 3600 for position in positions]

    def get_number_of_stops(self, positions):
        num_stops = 0

        for position in positions:
            if position.rr == -1:
                num_stops += 1

        return num_stops

    def get_number_of_profits(self, positions):
        num_profits = 0

        for position in positions:
            if position.rr > 0:
                num_profits += 1

        return num_profits

    def get_win_rate(self, positions):
        num_profits = self.get_number_of_profits(positions)
        num_positions = num_profits + self.get_number_of_stops(positions)
        return num_profits / num_positions

    def get_longest_streak(self, positions):
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

    def print(self):
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
        
        
class BarStats:
    def __init__(self, config):
        self.formatter = config.formatter
        self.bar_stats_names = config.bar_stats_names

    def calculate(self, match):
        """
        output = {
            stat: {
                'short_title': '',
                'long_title': '',
                'left': {
                    'value': 123,
                    'perc': 50,
                },
                'right': {
                    'value': 321,
                    'perc': 50,
                }
            },
            stat2: ...
        }
        """
        team1 = match.team1.data
        team2 = match.team2.data
        match = match.data

        comparison_stats = self.get_comparison_stats(
            self.get_team_stats(team1, match),
            self.get_team_stats(team2, match)
        )
        return self.formatter.bar_stat_format(comparison_stats, self.bar_stats_names)

    def get_team_stats(self, team, match):
        stats = {}
        t = match.protocols.get(team=team)
        for stat in self.bar_stats_names.keys():
            stats[stat] = self.formatter.chart_stat_format(t.__dict__.get(stat))
        return stats

    def get_comparison_stats(self, team1_stats, team2_stats):
        comparison_stats = {}
        for stat, team1_value, team2_value in zip(team1_stats.keys(), team1_stats.values(), team2_stats.values()):
            sum_value = team1_value + team2_value
            if not sum_value:
                left_perc = 0
                right_perc = 0
            else:
                left_perc = int(team1_value / sum_value * 100)
                right_perc = int(team2_value / sum_value * 100)
            comparison_stats[stat] = {
                'short_title': self.bar_stats_names[stat][0],
                'long_title': self.bar_stats_names[stat][1],
                'left_value': team1_value,
                'left_perc': left_perc,
                'right_value': team2_value,
                'right_perc': right_perc
            }
        return comparison_stats

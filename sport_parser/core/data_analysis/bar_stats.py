from sport_parser.core.exceptions import UnableToCalculateBarStats
from sport_parser.core.models import MatchModel


class BarStats:
    """
    Класс для расчета статистики, отображаемой в виде полос.

    :param stat_names: параметры расчета статистики, полученные из конфига.
    :param formatter: экземпляр класса форматирования результатов.
    """

    def __init__(self, config):
        self.formatter = config.formatter
        self.bar_stats_names = config.bar_stats_names
        self.live_bar_stats_names = config.live_bar_stats_names

    def match_stats_calculate(self, match: MatchModel):
        """
        Рассчитывает статистику для команды.

        :param match: строка матча модели MatchModel.
        :return: рассчитанная статистика.
        """
        if match.status != 'finished':
            raise UnableToCalculateBarStats
        comparison_stats = self._get_comparison_stats(
            self._get_team_stats(match.home_team, match),
            self._get_team_stats(match.guest_team, match)
        )
        return self.formatter.bar_stat_format(comparison_stats, self.bar_stats_names)

    def _get_team_stats(self, team, match):
        stats = {}
        t = match.protocols.get(team=team)
        for stat in self.bar_stats_names.keys():
            stats[stat] = self.formatter.chart_stat_format(t.__dict__.get(stat))
        return stats

    def _get_comparison_stats(self, team1_stats, team2_stats):
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


class LiveBarStats(BarStats):
    def calculate(self, match_data):
        comparison_stats = self._get_comparison_stats(
            self.get_team_live_stats(match_data['row_home']),
            self.get_team_live_stats(match_data['row_guest'])
        )
        return self.formatter.bar_stat_format(comparison_stats, self.live_bar_stats_names)

    def get_team_live_stats(self, data):
        stats = {}
        for stat in self.live_bar_stats_names.keys():
            stats[stat] = self.formatter.live_bar_stat_format(data[stat])
        return stats

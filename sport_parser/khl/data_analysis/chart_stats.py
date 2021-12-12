import datetime

from .formatter import Formatter


class ChartStats:
    def __init__(self, *, config):
        self.formatter = config.formatter(config=config)
        self.stat_names = config.chart_stats_names

    def calculate(self, team_list):
        stat_list = [*self.stat_names.keys()]
        if len(team_list) > 1:
            team_stats = self.get_team_stats_per_day(team_list[0], stat_list)
            opponent_stats = self.get_team_stats_per_day(team_list[1], stat_list)
            self_headers = [team_list[0].data.name for _ in self.stat_names]
            opponent_headers = [team_list[1].data.name for _ in self.stat_names]
        else:
            team_stats = self.get_team_stats_per_day(team_list, stat_list)
            opponent_stats = self.get_opp_stats_per_day(team_list, stat_list)
            self_headers = [value[0] for value in self.stat_names.values()]
            opponent_headers = [f'{value[0]}(A)' for value in self.stat_names.values()]

        while len(team_stats) != len(opponent_stats):
            if len(team_stats) < len(opponent_stats):
                opponent_stats.pop()
            else:
                team_stats.pop()

        output_stats = [[*self_headers, *opponent_headers]]

        for index, value, in enumerate(team_stats):
            value.extend(opponent_stats[index])
            output_stats.append(value)

        return output_stats

    def get_team_stats_per_day(self, team, stat_list):
        protocol_list = team.get_self_protocol_list()
        values_list = protocol_list.values_list(*stat_list)
        return [[self._format(stat) for stat in day] for day in values_list]

    def get_opp_stats_per_day(self, team, stat_list):
        protocol_list = team.get_opponent_protocol_list()
        values_list = protocol_list.values_list(*stat_list)
        return [[self._format(stat) for stat in day] for day in values_list]

    def _format(self, stat):
        if type(stat) == datetime.time:
            return self.formatter.time_to_sec(stat)
        else:
            return stat

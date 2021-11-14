import datetime

from .formatter import Formatter


class ChartStats:
    formatter = Formatter()
    stat_names = {
        'sh': ('Sh', 'int'),
        'sog': ('Sog', 'int'),
        'g': ('G', 'int'),
        'blocks': ('Blocks', 'int'),
        'penalty': ('Penalty', 'int'),
        'hits': ('Hits', 'int'),
        'time_a': ('TimeA', 'time'),
    }

    def calculate(self, team):
        stat_list = [*self.stat_names.keys()]
        team_stats = self.get_team_stats_per_day(team, stat_list)
        opponent_stats = self.get_opp_stats_per_day(team, stat_list)

        self_headers = [value[0] for value in self.stat_names.values()]
        opponent_headers = [f'{value[0]}(A)' for value in self.stat_names.values()]

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

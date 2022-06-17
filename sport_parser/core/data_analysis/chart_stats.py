import datetime

from sport_parser.core.data_analysis.formatter import Formatter
from sport_parser.core.models import TeamModel, MatchModel


class ChartStats:
    """
    Класс для расчета статистики, отображаемой в виде графиков.
    Рассчитывает статистику для команды или матча, из которой формируются таблицы в js.
    При расчете статистики для команды, названиями графиков указываются названия параметров.
    При расчете статистики для матча, названиями графиков указываются названия команд.

    :param stat_names: параметры расчета статистики, полученные из конфига.
    :param formatter: экземпляр класса форматирования результатов.
    """

    _stat_list: list
    _short_name_list: list
    _full_name_list: list

    def __init__(
            self,
            stat_names: dict,
            formatter: Formatter
    ):
        self.formatter = formatter
        self._parse_stats(stat_names)

    def team_stats_calculate(self, team: TeamModel):
        """
        Рассчитывает статистику для команды.

        :param team: строка команды модели TeamModel.
        :return: рассчитанная статистика.
        """

        team_stats = self._get_team_stats_per_day(team)
        opponent_stats = self._get_opp_stats_per_day(team)

        self_headers = self._short_name_list
        opponent_headers = [f'{value}(A)' for value in self._short_name_list]
        headers = [*self_headers, *opponent_headers]

        return self._calculate(headers, team_stats, opponent_stats)

    def match_stats_calculate(self, match: MatchModel):
        """
        Рассчитывает статистику для команды.

        :param match: строка матча модели MatchModel.
        :return: рассчитанная статистика.
        """

        team1 = match.home_team
        team2 = match.guest_team

        team1_stats = self._get_team_stats_per_day(team1)
        team2_stats = self._get_team_stats_per_day(team2)

        team1_headers = [team1.name for _ in self._short_name_list]
        team2_headers = [team2.name for _ in self._short_name_list]
        headers = [*team1_headers, *team2_headers]

        return self._calculate(headers, team1_stats, team2_stats)

    def _calculate(self, headers, team1_stats, team2_stats) -> list:
        output_stats = [headers]
        while len(team1_stats) != len(team2_stats):
            if len(team1_stats) < len(team2_stats):
                team2_stats.pop()
            else:
                team1_stats.pop()
        for index, value, in enumerate(team1_stats):
            value.extend(team2_stats[index])
            output_stats.append(value)
        return [output_stats, self._short_name_list, self._full_name_list]

    def _get_team_stats_per_day(self, team):
        protocol_list = team.protocols.all().order_by('updated')

        values_list = protocol_list.values_list(*self._stat_list)
        return [[self._format(stat) for stat in day] for day in values_list]

    def _get_opp_stats_per_day(self, team):
        match_list = team.matches.filter(status='finished')
        all_protocol_list = team.season.protocols.all()
        protocol_list = all_protocol_list.filter(match__in=match_list).exclude(team=team)

        values_list = protocol_list.values_list(*self._stat_list)
        return [[self._format(stat) for stat in day] for day in values_list]

    def _parse_stats(self, stat_names):
        self._stat_list = []
        self._short_name_list = []
        self._full_name_list = []
        for stat, values in stat_names.items():
            self._stat_list.append(stat)
            self._short_name_list.append(values[0])
            self._full_name_list.append(values[1])

    def _format(self, stat):
        if type(stat) == datetime.time:
            return self.formatter.time_to_sec(stat)
        else:
            return stat

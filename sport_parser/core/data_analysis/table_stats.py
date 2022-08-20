import datetime
from django.db.models import Q

from .formatter import Formatter
from ..models import SeasonModel, MatchModel


class TableStats:
    """
    Класс для расчета статистики, отображаемой в виде таблицы.
    При расчете статистики для сезона рассчитывается статистика для всех команд.
    При расчете статистики для матча рассчитывается статистика для двух команд матча.

    :param stat_names: параметры рассчета статистики, полученные из конфига.
    :param formatter: экземпляр класса форматирования результатов.
    """

    _team_stats: dict
    _opponent_stats: dict
    _extra_stats: dict

    def __init__(
            self,
            stat_names: dict,
            stat_types: dict,
            formatter: Formatter,
    ):
        self.formatter = formatter
        self.stat_names = stat_names
        self._parse_stats(stat_types)

    def season_stats_calculate(self, season: SeasonModel):
        """
        Рассчитывает статистику для сезона.

        :param season: строка сезона модели SeasonModel/
        :return: рассчитанная статистика.
        """
        team_list = season.teams.all().order_by('name')
        match_list = season.matches.filter(status='finished')
        return self._calculate_table_stats(team_list, match_list)

    def match_stats_calculate(self, match: MatchModel):
        """
        Рассчитывает статистика для матча.

        :param match: строка матча модели MatchModel.
        :return: рассчитанная статистика.
        """
        team_list = [match.home_team, match.guest_team]
        match_list = match.season.matches.filter(status='finished')
        return self._calculate_table_stats(team_list, match_list)

    def _calculate_table_stats(self, team_list, match_list):
        table_headers = ['Team']
        for name in self.stat_names.values():
            table_headers.append(name[0])

        stats = [table_headers]
        for team in team_list:
            team_stats = self._get_team_season_stats(team, match_list)
            stats.append(team_stats)

        return stats

    def _get_team_season_stats(self, team, match_list):
        team_match_list = match_list.filter(Q(home_team=team) | Q(guest_team=team))
        protocol_list = team.season.protocols.all()
        team_protocol_list = team.protocols.all().order_by('updated')
        opponent_protocol_list = protocol_list.filter(match__in=team_match_list).exclude(team=team)
        team_stats = {}

        if not protocol_list:
            team_stats = {stat: 0 for stat in self._team_stats.keys()}
            team_stats.update({stat: 0 for stat in self._opponent_stats.keys()})
            team_stats.update({stat: 0 for stat in self._extra_stats.keys()})
        else:
            for stat, mode in self._team_stats.items():
                team_stats[stat] = self._calculate_stat(stat, team_protocol_list, mode=mode)
            for stat, mode in self._opponent_stats.items():
                team_stats[stat] = self._calculate_stat(stat, opponent_protocol_list, mode=mode)
            for stat, expr in self._extra_stats.items():
                team_stats[stat] = eval(expr, {}, team_stats)

        team_stats = self.formatter.table_stat_format(team_stats, stat_names=self.stat_names)
        ordered_stat_list = []
        for stat in self.stat_names.keys():
            ordered_stat_list.append(team_stats[stat])

        return [team.id, team.name] + ordered_stat_list

    def _calculate_stat(self, stat, protocol_list, mode):
        stat_list = [protocol.__dict__[stat.split('__')[0]] for protocol in protocol_list]
        if mode == 'median':
            return self._get_median(stat_list)
        if mode == 'sum':
            return sum(stat_list)
        raise ValueError('Invalid mode')

    def _parse_stats(self, stats):
        self._team_stats = {}
        self._opponent_stats = {}
        self._extra_stats = {}

        for stat, mode in stats.items():
            if '__a' in stat:
                self._opponent_stats[stat] = mode
            elif '__e' in stat:
                self._extra_stats[stat] = mode
            else:
                self._team_stats[stat] = mode

    def _get_median(self, items: list) -> float:
        """Возвращает медиану списка"""
        items.sort()
        if len(items) % 2 != 0:
            median = int(len(items) // 2)
            if type(items[median]) == datetime.time:
                return round(self.formatter.time_to_sec(items[median]), 0)
            return items[median]
        median = int(len(items) / 2)
        if type(items[median]) == datetime.time:
            time1 = self.formatter.time_to_sec(items[median])
            time2 = self.formatter.time_to_sec(items[median - 1])
            return round((time1 + time2) / 2, 0)
        return (items[median] + items[median - 1]) / 2

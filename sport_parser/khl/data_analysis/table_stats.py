from django.db.models import Sum
import datetime

from .formatter import Formatter


class TableStats:
    formatter = Formatter()
    stats = {
        'sh': 'median',
        'sog': 'median',
        'g': 'median',
        'time_a': 'median',
        'hits': 'median',
        'blocks': 'median',
        'penalty': 'median',

        'sh__a': 'median',
        'sog__a': 'median',
        'g__a': 'median',
        'time_a__a': 'median',
        'blocks__a': 'median',

        'faceoff': 'sum',
        'faceoff__a': 'sum',

        'sh__e': 'sh / (sh + sh__a) * 100',
        'sog__e': 'sog / sh * 100',
        'faceoff__e': 'faceoff / (faceoff + faceoff__a) * 100',
        'blocks__e': 'blocks / (blocks + blocks__a) * 100',
        'dev__e': '(1 - (sog__a / sh__a)) * 100',
        'time_a__e': 'time_a / (time_a + time_a__a) * 100',
        'pdo__e': '((sh / (sh + sh__a)) + (sog / sh)) * 100',
    }
    #
    stat_names = {
        'sh': ('Sh', 'int'),
        'sh__a': ('Sh(A)', 'int'),
        'sh__e': ('Sh%', 'percent'),
        'sog': ('SoG', 'int'),
        'sog__a': ('SoG(A)', 'int'),
        'sog__e': ('AQ', 'percent'),
        'g': ('G', 'int'),
        'g__a': ('G(A)', 'int'),
        'faceoff__e': ('FaceOff%', 'percent'),
        'time_a': ('TimeA', 'time'),
        'time_a__a': ('TimeA(A)', 'time'),
        'time_a__e': ('TimeA%', 'percent'),
        'dev__e': ('DEV%', 'percent'),
        'pdo__e': ('PDO%', 'percent'),
        'hits': ('Hits', 'int'),
        'blocks': ('Blocks', 'int'),
        'blocks__a': ('Blocks(A)', 'int'),
        'blocks__e': ('Blocks%', 'percent'),
        'penalty': ('Penalty', 'int'),
    }

    match_stats_names = {
        'sh': ('Sh', 'int'),
        'sog': ('SoG', 'int'),
        'g': ('G', 'int'),
        'faceoff': ('FaceOff', 'int'),
        'faceoff_p': ('FaceOff%', 'percent'),
        'hits': ('Hits', 'int'),
        'blocks': ('Blocks', 'int'),
        'penalty': ('Penalty', 'int'),
        'time_a': ('TimeA', 'time'),
    }

    def season_stats_calculate(self, match_list, team_list, protocol_list):
        self.protocol_list = protocol_list
        self._parse_stats()

        table_headers = ['Team']
        for name in self.stat_names.values():
            table_headers.append(name[0])

        stats = [table_headers]
        for team in team_list:
            team_stats = [team.id, team.name]
            team_stats.extend(self.get_team_season_stats(team, match_list))
            stats.append(team_stats)

        return stats

    def match_stats_calculate(self, match):
        table_headers = ['Team']
        for name in self.match_stats_names.values():
            table_headers.append(name[0])

        stats = [table_headers]
        for team in match.teams.all():
            team_stats = [team.id, team.name]
            team_stats.extend(self.get_team_match_stats(team, match))
            stats.append(team_stats)

        return stats

    def get_team_match_stats(self, team, match):
        stats = {}
        t = match.protocols.get(team=team)
        for stat in self.match_stats_names.keys():
            stats[stat] = t.__dict__.get(stat)

        stats = self.formatter.table_stat_format(stats, stat_names=self.match_stats_names)
        ordered_stat_list = []
        for stat, _ in self.match_stats_names.items():
            ordered_stat_list.append(stats[stat])

        return ordered_stat_list

    def get_team_season_stats(self, team, match_list):
        team_match_list = match_list.filter(teams=team)
        team_stats = {}
        for stat, mode in self._team_stats.items():
            team_stats[stat] = self.get_team_stat(team, stat, team_match_list, mode=mode)

        for stat, mode in self._opponent_stats.items():
            team_stats[stat] = self.get_opponent_stat(team, stat[:-3], team_match_list, mode=mode)

        for stat, expr in self._extra_stats.items():
            team_stats[stat] = eval(expr, {}, team_stats)

        team_stats = self.formatter.table_stat_format(team_stats, stat_names=self.stat_names)
        ordered_stat_list = []
        for stat, _ in self.stat_names.items():
            ordered_stat_list.append(team_stats[stat])

        return ordered_stat_list

    def get_team_stat(self, team, stat, match_list, *, mode):
        """В зависимости от mode возвращает медиану или сумму параметра stat команды team в матчах match_list
        mode:
            median - рассчитать медиану
            sum - рассчитать сумму
        """
        stat_list = self.protocol_list.filter(match__in=match_list).filter(team=team).order_by(stat)
        return self._calculate_stat(stat, stat_list, mode=mode)

    def get_opponent_stat(self, team, stat, match_list, *, mode):
        """В зависимости от mode возвращает медиану или сумму параметра stat противника команды team в матчах match_list
        mode:
            median - рассчитать медиану
            sum - рассчитать сумму
        """
        stat_list = self.protocol_list.filter(match__in=match_list).exclude(team=team).order_by(stat)
        return self._calculate_stat(stat, stat_list, mode=mode)

    def _calculate_stat(self, stat, stat_list, mode):
        if mode == 'median':
            stats = stat_list.values_list(stat, flat=True)
            return self.get_median([x for x in stats])
        if mode == 'sum':
            calc_stat = stat_list.aggregate(Sum(stat))
            return calc_stat[f'{stat}__sum']
        raise ValueError('Invalid mode')

    def _parse_stats(self):
        self._team_stats = {}
        self._opponent_stats = {}
        self._extra_stats = {}

        for stat, mode in self.stats.items():
            if '__a' in stat:
                self._opponent_stats[stat] = mode
            elif '__e' in stat:
                self._extra_stats[stat] = mode
            else:
                self._team_stats[stat] = mode

    def get_median(self, items):
        """Возвращает медиану списка"""
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

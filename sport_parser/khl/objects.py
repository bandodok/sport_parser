from django.db.models import Max
import datetime

from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.data_analysis.table_stats import TableStats
from sport_parser.khl.data_analysis.chart_stats import ChartStats
from sport_parser.khl.models import KHLSeason, KHLMatch, KHLTeams, KHLProtocol


class ModelList:
    season_model = KHLSeason
    match_model = KHLMatch
    team_model = KHLTeams
    protocol_model = KHLProtocol


class Season:
    TableStats = TableStats()
    ChartStats = 'ChartStats'
    formatter = Formatter()
    season_does_not_exist = False
    models = ModelList()

    def __init__(self, season_id):
        try:
            self.data = self.models.season_model.objects.get(id=season_id)
        except self.models.season_model.DoesNotExist:
            self.season_does_not_exist = True

    def get_match_list(self):
        return self.data.matches.all()

    def get_team_list(self):
        return self.data.teams.all().order_by('name')

    def get_protocol_list(self):
        return self.models.protocol_model.objects.filter(match__season_id=self.data)

    def get_last_matches(self, num):
        return self.data.matches.filter(finished=True).order_by('-date')[:num]

    def get_json_last_matches(self, num):
        lats_matches = self.get_last_matches(num)
        return self.formatter.get_json_last_matches_info(lats_matches)

    def get_future_matches(self, num):
        return self.data.matches.filter(finished=False).order_by('date')[:num]

    def get_json_future_matches(self, num):
        future_matches = self.get_last_matches(num)
        return self.formatter.get_json_future_matches_info(future_matches)

    def last_updated(self, *, update=False):
        """Возвращает дату последнего обновления таблицы матчей
        При update=True обновляет эту дату на текущую"""
        last_update = self.data.matches.aggregate(Max('updated'))['updated__max']
        if update:
            last_matches = self.get_match_list().filter(updated=last_update)
            last = last_matches[len(last_matches) - 1]
            last.updated = datetime.datetime.now()
            last.save()
        return last_update

    def get_stat_fields_list(self):
        fields = self.data.matches.all()[0].protocols.all()[0].__dict__
        for field in ['_state', 'id', 'created', 'updated', 'team_id', 'match_id']:
            fields.pop(field)
        return fields

    def get_table_stats(self, *, match_list=None, team_list=None, protocol_list=None):
        if not match_list:
            match_list = self.get_match_list()
        if not team_list:
            team_list = self.get_team_list()
        if not protocol_list:
            protocol_list = self.get_protocol_list()
        return self.TableStats.season_stats_calculate(match_list, team_list, protocol_list)


class Team:
    TableStats = TableStats()
    ChartStats = ChartStats()
    season_class = Season
    formatter = Formatter()
    models = ModelList()

    def __init__(self, team_id):
        self.data = self.models.team_model.objects.get(id=team_id)

    def __len__(self):
        return 1

    def get_match_list(self):
        return self.data.matches.all()

    def get_self_protocol_list(self):
        return self.data.protocols.all()

    def get_opponent_protocol_list(self):
        match_list = self.get_match_list()
        protocol_list = self.models.protocol_model.objects.filter(match__in=match_list).exclude(team=self.data)
        return protocol_list.order_by('match__date')

    def get_last_matches(self, num, *, exclude=0):
        return self.data.matches.filter(finished=True).exclude(id=exclude).order_by('-date')[:num]

    def get_json_last_matches(self, num, *, exclude=0):
        lats_matches = self.get_last_matches(num, exclude=exclude)
        return self.formatter.get_json_last_matches_info(lats_matches)

    def get_future_matches(self, num, *, exclude=0):
        return self.data.matches.filter(finished=False).exclude(id=exclude).order_by('date')[:num]

    def get_json_future_matches(self, num, *, exclude=0):
        future_matches = self.get_future_matches(num, exclude=exclude)
        return self.formatter.get_json_future_matches_info(future_matches)

    def get_table_stats(self):
        season = self.season_class(self.data.season_id)
        return season.get_table_stats(team_list=[self.data])

    def get_chart_stats(self, team_list=None):
        if not team_list:
            team_list = self
        return self.ChartStats.calculate(team_list)

    def get_another_season_team_ids(self):
        """Возвращает список id команды для разных сезонов"""
        name = self.data.name
        season_list = self.models.team_model.objects.filter(name=name).order_by('season').values('id', 'season')
        return [x for x in season_list]


class Match:
    TableStats = TableStats()
    ChartStats = ChartStats()
    season_class = Season
    team_class = Team
    formatter = Formatter()
    models = ModelList()

    def __init__(self, match_id):
        self.data = self.models.match_model.objects.get(id=match_id)
        self._set_teams()
        self._set_exclude()

    def get_match_stats(self):
        if not self.data.finished:
            return 'The match is not over yet'
        return self.TableStats.match_stats_calculate(self.data)

    def get_team1_score_by_period(self):
        if not self.data.finished:
            return 'The match is not over yet'
        protocol = self.team1.data.protocols.get(match=self.data)
        return {
            'match': self.get_team1_score(),
            'p1': protocol.g_1,
            'p2': protocol.g_2,
            'p3': protocol.g_3,
            'ot': protocol.g_ot,
            'b': protocol.g_b,
        }

    def get_team1_score(self):
        if not self.data.finished:
            return 'The match is not over yet'
        goals = self.team1.data.protocols.get(match=self.data).g
        penalties = self.team1.data.protocols.get(match=self.data).g_b
        return goals + penalties

    def get_team2_score_by_period(self):
        if not self.data.finished:
            return 'The match is not over yet'
        protocol = self.team2.data.protocols.get(match=self.data)
        return {
            'match': self.get_team2_score(),
            'p1': protocol.g_1,
            'p2': protocol.g_2,
            'p3': protocol.g_3,
            'ot': protocol.g_ot,
            'b': protocol.g_b,
        }

    def get_team2_score(self):
        if not self.data.finished:
            return 'The match is not over yet'
        goals = self.team2.data.protocols.get(match=self.data).g
        penalties = self.team2.data.protocols.get(match=self.data).g_b
        return goals + penalties

    def get_team1_last_matches(self, num):
        return self.team1.get_json_last_matches(num, exclude=self._exclude)

    def get_team1_json_last_matches(self, num):
        return self.team1.get_json_last_matches(num, exclude=self._exclude)

    def get_team1_future_matches(self, num):
        return self.team1.get_json_future_matches(num, exclude=self._exclude)

    def get_team1_json_future_matches(self, num):
        return self.team1.get_json_future_matches(num, exclude=self._exclude)

    def get_team2_last_matches(self, num):
        return self.team2.get_json_last_matches(num, exclude=self._exclude)

    def get_team2_json_last_matches(self, num):
        return self.team2.get_json_last_matches(num, exclude=self._exclude)

    def get_team2_future_matches(self, num):
        return self.team2.get_json_future_matches(num, exclude=self._exclude)

    def get_team2_json_future_matches(self, num):
        return self.team2.get_json_future_matches(num, exclude=self._exclude)

    def get_table_stats(self):
        season = self.season_class(self.data.season_id)
        return season.get_table_stats(team_list=[self.team1.data, self.team2.data])

    def get_chart_stats(self):
        team_list = (self.team1, self.team2)
        return self.ChartStats.calculate(team_list)

    def _set_teams(self):
        team1, team2 = self.data.teams.all()
        self.team1 = self.team_class(team1.id)
        self.team2 = self.team_class(team2.id)

    def _set_exclude(self):
        self._exclude = 0
        if self.data.finished:
            self._exclude = self.data.id

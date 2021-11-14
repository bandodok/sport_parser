from django.db.models import Sum, Max
import datetime

from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.data_analysis.table_stats import TableStats
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

    def __init__(self, season_id):
        self.models = ModelList()
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

    def get_future_matches(self, num):
        return self.data.matches.filter(finished=False).order_by('date')[:num]

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
        return self.TableStats.calculate(match_list, team_list, protocol_list)


class Team:

    def __init__(self, model, team_id):
        self.model = model
        self.data = model.objects.get(id=team_id)

    def get_match_list(self):
        return self.data.matches.all()

    def get_last_matches(self, num):
        return self.data.matches.filter(finished=True).order_by('-date')[:num]

    def get_future_matches(self, num):
        return self.data.matches.filter(finished=False).order_by('date')[:num]

    def season_stats_overall(self):
        pass

    def season_stats_per_day(self):
        pass

    def get_chart_stats(self):
        pass


class Match:

    def __init__(self, model, match_id):
        self.model = model
        self.data = model.objects.get(match_id=match_id)
        self._set_teams()

    def get_current_match_stats(self):
        pass

    def _set_teams(self):
        team1, team2 = self.data.teams.all()
        self.team1 = Team(self.model, team1.id)
        self.team2 = Team(self.model, team2.id)

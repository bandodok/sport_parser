from django.db.models import Max
import datetime


class Season:
    season_does_not_exist = False

    def __init__(self, season_id, *, config):
        self.TableStats = config.TableStats(config=config)
        self.formatter = config.formatter(config=config)
        self.models = config.models
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
        return self.data.matches.filter(status='finished').order_by('-date')[:num]

    def get_json_last_matches(self, num):
        lats_matches = self.get_last_matches(num)
        return self.formatter.get_json_last_matches_info(lats_matches)

    def get_future_matches(self, num):
        return self.data.matches.filter(status='scheduled').order_by('date')[:num]

    def get_json_future_matches(self, num):
        future_matches = self.get_future_matches(num)
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
        return [key for key, value in fields.items()]

    def get_table_stats(self, *, match_list=None, team_list=None, protocol_list=None):
        if not match_list and not team_list and not protocol_list:
            return self.data.table_data
        if not match_list:
            match_list = self.get_match_list()
        if not team_list:
            team_list = self.get_team_list()
        if not protocol_list:
            protocol_list = self.get_protocol_list()
        return self.TableStats.season_stats_calculate(match_list, team_list, protocol_list)

    def update_season_table_stats(self):
        data = self.get_table_stats(match_list=self.get_match_list())
        self.data.table_data = data
        self.data.save()


class Team:
    def __init__(self, team_id, *, config):
        self.config = config
        self.TableStats = config.TableStats(config=config)
        self.ChartStats = config.ChartStats(config=config)
        self.season_class = config.season_class
        self.formatter = config.formatter(config=config)
        self.models = config.models

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
        return self.data.matches.filter(status='finished').exclude(id=exclude).order_by('-date')[:num]

    def get_json_last_matches(self, num, *, exclude=0):
        lats_matches = self.get_last_matches(num, exclude=exclude)
        return self.formatter.get_json_last_matches_info(lats_matches)

    def get_future_matches(self, num, *, exclude=0):
        return self.data.matches.filter(status='scheduled').exclude(id=exclude).order_by('date')[:num]

    def get_json_future_matches(self, num, *, exclude=0):
        future_matches = self.get_future_matches(num, exclude=exclude)
        return self.formatter.get_json_future_matches_info(future_matches)

    def get_table_stats(self):
        season = self.season_class(self.data.season_id, config=self.config)
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
    def __init__(self, match_id, *, config):
        self.config = config
        self.TableStats = config.TableStats(config=config)
        self.ChartStats = config.ChartStats(config=config)
        self.BarStats = config.BarStats(config=config)
        self.LiveBarStats = config.LiveBarStats(config=config)
        self.season_class = config.season_class
        self.team_class = config.team_class
        self.formatter = config.formatter(config=config)
        self.models = config.models

        self.data = self.models.match_model.objects.get(id=match_id)
        self._set_teams()
        self._set_exclude()

    def get_team1_score_by_period(self):
        if self.data.status != 'finished':
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
        if self.data.status != 'finished':
            return 'The match is not over yet'
        goals = self.team1.data.protocols.get(match=self.data).g
        penalties = self.team1.data.protocols.get(match=self.data).g_b
        return goals + penalties

    def get_team2_score_by_period(self):
        if self.data.status != 'finished':
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
        if self.data.status != 'finished':
            return 'The match is not over yet'
        goals = self.team2.data.protocols.get(match=self.data).g
        penalties = self.team2.data.protocols.get(match=self.data).g_b
        return goals + penalties

    def get_team1_last_matches(self, num):
        return self.team1.get_json_last_matches(num, exclude=self._exclude)

    def get_team1_future_matches(self, num):
        return self.team1.get_json_future_matches(num, exclude=self._exclude)

    def get_team2_last_matches(self, num):
        return self.team2.get_json_last_matches(num, exclude=self._exclude)

    def get_team2_future_matches(self, num):
        return self.team2.get_json_future_matches(num, exclude=self._exclude)

    def get_match_stats(self):
        if self.data.status != 'finished':
            return 'The match is not over yet'
        return self.TableStats.match_stats_calculate(self.data)

    def get_table_stats(self):
        season = self.season_class(self.data.season_id, config=self.config)
        return season.get_table_stats(team_list=[self.team1.data, self.team2.data])

    def get_bar_stats(self):
        if self.data.status != 'finished':
            return 'The match is not over yet'
        return self.BarStats.calculate(self)

    def get_live_bar_stats(self, match_data):
        return self.LiveBarStats.calculate(match_data)

    def get_chart_stats(self):
        team_list = (self.team1, self.team2)
        return self.ChartStats.calculate(team_list)

    def _get_m2m_table_name(self):
        meta = self.models.match_model._meta
        app_label = meta.app_label
        match_model = meta.model_name
        team_model = meta.many_to_many[0].column
        return f'{app_label}_{match_model}_{team_model}'

    def _set_teams(self):
        m2m_table = self._get_m2m_table_name()
        team1, team2 = self.data.teams.all().extra(select={'add_id': f'{m2m_table}.id'}).order_by('add_id')
        self.team1 = self.team_class(team1.id, config=self.config)
        self.team2 = self.team_class(team2.id, config=self.config)

    def _set_exclude(self):
        self._exclude = 0
        if self.data.status == 'finished':
            self._exclude = self.data.id

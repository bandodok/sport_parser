from django.db.models import Max
import datetime
from django.db.models import Q

from sport_parser.core.data_analysis.formatter import Formatter
from sport_parser.core.models import ModelList, SeasonModel, TeamModel, MatchModel


class Season:
    """
    Класс представления информации по сезону.

    :param data: данные сезона в формате строки модели SeasonModel
    :param formatter: экземпляр класса Formatter, форматирующий выходные данные
    :param models: экземпляр класса ModelList, содержащий модели базы данных
    """

    def __init__(
            self,
            data: SeasonModel,
            formatter: Formatter,
            models: ModelList
    ):
        self.formatter = formatter
        self.models = models
        self.data = data

    def get_match_list(self):
        return self.data.matches.all()

    def get_last_matches(self, num):
        return self.data.matches.filter(status='finished').order_by('-date')[:num]

    def get_json_last_matches(self, num):
        lats_matches = self.get_last_matches(num)
        return self.formatter.get_json_matches_info(lats_matches)

    def get_future_matches(self, num):
        return self.data.matches.filter(status='scheduled').order_by('date')[:num]

    def get_json_future_matches(self, num):
        future_matches = self.get_future_matches(num)
        return self.formatter.get_json_matches_info(future_matches)

    def get_live_matches(self):
        return self.data.matches\
            .filter(Q(status='live') | Q(status='game over'))\
            .order_by('date')

    def get_json_live_matches(self):
        live_matches = self.get_live_matches()
        return self.formatter.get_json_matches_info(live_matches)

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

    def get_table_stats(self):
        return self.data.table_data


class Team:
    """
    Класс представления информации по команде.

    :param data: данные команды в формате строки модели TeamModel
    :param formatter: экземпляр класса Formatter, форматирующий выходные данные
    :param models: экземпляр класса ModelList, содержащий модели базы данных
    """

    def __init__(
            self,
            data: TeamModel,
            formatter: Formatter,
            models: ModelList
    ):
        self.formatter = formatter
        self.models = models
        self.data = data

    def get_last_matches(self, num, *, exclude=0):
        return self.data.matches.filter(status='finished').exclude(id=exclude).order_by('-date')[:num]

    def get_json_last_matches(self, num, *, exclude=0):
        lats_matches = self.get_last_matches(num, exclude=exclude)
        return self.formatter.get_json_matches_info(lats_matches)

    def get_future_matches(self, num, *, exclude=0):
        return self.data.matches.filter(status='scheduled').exclude(id=exclude).order_by('date')[:num]

    def get_json_future_matches(self, num, *, exclude=0):
        future_matches = self.get_future_matches(num, exclude=exclude)
        return self.formatter.get_json_matches_info(future_matches)

    def get_chart_stats(self):
        return self.data.chart_data

    def get_another_season_team_ids(self):
        """Возвращает список id команды для разных сезонов"""
        name = self.data.name
        season_list = self.models.team_model.objects.filter(name=name).order_by('season').values('id', 'season')
        return [x for x in season_list]


class Match:
    """
    Класс представления информации по матчу.

    :param data: данные матча в формате строки модели MatchModel
    :param formatter: экземпляр класса Formatter, форматирующий выходные данные
    :param models: экземпляр класса ModelList, содержащий модели базы данных
    :param team1: экземпляр класса Team, содержит информацию по домашней команде
    :param team2: экземпляр класса Team, содержит информацию по гостевой команде
    """

    def __init__(
            self,
            data: MatchModel,
            formatter: Formatter,
            models: ModelList,
            team1: Team,
            team2: Team,
    ):
        self.formatter = formatter
        self.models = models
        self.team1 = team1
        self.team2 = team2
        self.data = data
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

    def get_table_stats(self):
        return self.data.table_data

    def get_bar_stats(self):
        return self.data.bar_data

    def get_chart_stats(self):
        return self.data.chart_data

    def _set_exclude(self):
        self._exclude = 0
        if self.data.status == 'finished':
            self._exclude = self.data.id

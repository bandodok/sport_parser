from django.db.models import Max

from sport_parser.core.configs import ConfigType
from sport_parser.core.data_analysis.bar_stats import BarStats
from sport_parser.core.data_analysis.chart_stats import ChartStats
from sport_parser.core.data_analysis.formatter import Formatter
from sport_parser.core.data_analysis.stats_updater import StatsUpdater
from sport_parser.core.data_analysis.table_stats import TableStats
from sport_parser.core.data_taking.db import DB
from sport_parser.core.data_taking.parser import Parser, ParseMethods
from sport_parser.core.exceptions import SeasonDoesNotExist, TeamDoesNotExist, MatchDoesNotExist
from sport_parser.core.models import ModelList, SeasonModel, TeamModel, MatchModel
from sport_parser.core.objects import Season, Team, Match
from sport_parser.core.updater import Updater


class Creator:
    """
    Класс для создания объектов приложения.

    :param config: конфиг приложения в формате ConfigType
    """
    def __init__(self, config: ConfigType):
        self.config = config.value

    def get_season_class(self, season_id: int) -> Season:
        if season_id == 0:
            season_id = self.config.models.season_model.objects.aggregate(Max('id'))['id__max']
        data = self._get_season_data(season_id)
        return self.config.season_class(
            data=data,
            formatter=self.get_formatter(),
            models=self.get_model_list()
        )

    def get_team_class(self, team_id: int) -> Team:
        if team_id == 0:
            team_id = self.config.models.team_model.objects.aggregate(Max('id'))['id__max']
        data = self._get_team_data(team_id)
        return self.config.team_class(
            data=data,
            formatter=self.get_formatter(),
            models=self.get_model_list()
        )

    def get_match_class(self, match_id: int) -> Match:
        if match_id == 0:
            match_id = self.config.models.match_model.objects.aggregate(Max('id'))['id__max']
        data = self._get_match_data(match_id)
        match = self.config.models.match_model.objects.get(id=match_id)
        team1 = match.home_team
        team2 = match.guest_team
        return self.config.match_class(
            data=data,
            formatter=self.get_formatter(),
            models=self.get_model_list(),
            team1=self.get_team_class(team1.id),
            team2=self.get_team_class(team2.id)
        )

    def get_updater(self) -> Updater:
        return self.config.updater(
            model_list=self.get_model_list(),
            parser=self.get_parser(),
            db=self.get_db(),
            stats_updater=self.get_stats_updater(),

            ignore=self.config.updater_ignore,
            league=self.config.name,
        )

    def get_parser(self) -> Parser:
        return self.config.parser(
            parse_method=ParseMethods[self.config.parse_method]
        )

    def get_stats_updater(self) -> StatsUpdater:
        return self.config.stats_updater(
            table_stats=self.get_table_stats(),
            chart_stats=self.get_chart_stats(),
            bar_stats=self.get_bar_stats(),
            db=self.get_db(),
        )

    def get_table_stats(self) -> TableStats:
        return self.config.table_stats(
            formatter=self.get_formatter(),
            stat_names=self.config.table_stats_names,
            stat_types=self.config.table_stats_types
        )

    def get_chart_stats(self) -> ChartStats:
        return self.config.chart_stats(
            formatter=self.get_formatter(),
            stat_names=self.config.chart_stats_names
        )

    def get_bar_stats(self) -> BarStats:
        return self.config.bar_stats(
            formatter=self.get_formatter(),
            stat_names=self.config.bar_stats_names,
            live_stat_names=self.config.live_bar_stats_names
        )

    def get_db(self) -> DB:
        return self.config.db(
            model_list=self.config.models,
            updated_team_names=self.config.updated_team_names
        )

    def get_model_list(self) -> ModelList:
        return self.config.models()

    def get_formatter(self) -> Formatter:
        return self.config.formatter(
            calendar_serializer=self.config.calendar_serializer
        )

    # методы для шаблонов
    def get_title(self):
        return self.config.title

    def get_league_title(self):
        return self.config.league_title

    def get_league_logo(self):
        return self.config.league_logo

    def get_background_image(self):
        return self.config.background_image

    def get_theme(self):
        return self.config.theme

    def get_glossary(self):
        return self.config.glossary

    def get_season_list(self):
        return list(self.config.models.season_model.objects.order_by('id').values_list('id', flat=True))

    # методы получения данных из моделей
    def _get_season_data(self, season_id: int) -> SeasonModel:
        model = self.config.models.season_model
        return self._get_data(season_id, model, SeasonDoesNotExist)

    def _get_team_data(self, team_id: int) -> TeamModel:
        model = self.config.models.team_model
        return self._get_data(team_id, model, TeamDoesNotExist)

    def _get_match_data(self, match_id: int) -> MatchModel:
        model = self.config.models.match_model
        return self._get_data(match_id, model, MatchDoesNotExist)

    @staticmethod
    def _get_data(item_id, model, exception):
        try:
            data = model.objects.get(id=item_id)
        except model.DoesNotExist:
            raise exception
        return data

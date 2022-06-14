from django.db.models import Max

from sport_parser.core.configs import ConfigType
from sport_parser.core.data_analysis.bar_stats import BarStats
from sport_parser.core.data_analysis.chart_stats import ChartStats
from sport_parser.core.data_analysis.formatter import Formatter
from sport_parser.core.data_analysis.stats_updater import StatsUpdater
from sport_parser.core.data_analysis.table_stats import TableStats
from sport_parser.core.data_taking.db import DB
from sport_parser.core.data_taking.parser import Parser
from sport_parser.core.models import ModelList
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
        return self.config.season_class(
            season_id=season_id,
            formatter=self.get_formatter(),
            models=self.get_model_list()
        )

    def get_team_class(self, team_id: int) -> Team:
        if team_id == 0:
            team_id = self.config.models.team_model.objects.aggregate(Max('id'))['id__max']
        return self.config.team_class(
            team_id=team_id,
            formatter=self.get_formatter(),
            models=self.get_model_list()
        )

    def get_match_class(self, match_id: int) -> Match:
        if match_id == 0:
            match_id = self.config.models.match_model.objects.aggregate(Max('id'))['id__max']
        match = self.config.models.match_model.objects.get(id=match_id)
        team1 = match.home_team
        team2 = match.guest_team
        return self.config.match_class(
            match_id=match_id,
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
        return self.config.parser()

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

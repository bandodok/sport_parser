from sport_parser.api.serializers import CalendarSerializer
from sport_parser.core.data_analysis.stats_updater import StatsUpdater
from sport_parser.khl.models import ModelList
from sport_parser.core.objects import Season, Team, Match
from sport_parser.core.data_analysis.chart_stats import ChartStats
from sport_parser.core.data_analysis.table_stats import TableStats
from sport_parser.core.models import LiveMatches
from sport_parser.core.data_analysis.bar_stats import BarStats
from sport_parser.core.data_analysis.formatter import Formatter
from sport_parser.core.data_taking.parser import Parser
from sport_parser.core.data_taking.db import DB
from sport_parser.core.updater import Updater


class Config:
    name: str
    title: str
    league_title: str
    league_logo: str
    background_image: str
    theme: str

    table_stats_names: dict
    table_stats_types: dict
    bar_stats_names: dict
    chart_stats_names: dict
    glossary: dict
    updated_team_names: dict = {}
    updater_ignore: list = []

    models: ModelList = ModelList
    live_match_model: LiveMatches = LiveMatches
    season_class: Season = Season
    team_class: Team = Team
    match_class: Match = Match
    stats_updater: StatsUpdater = StatsUpdater
    table_stats: TableStats = TableStats
    chart_stats: ChartStats = ChartStats
    bar_stats: BarStats = BarStats
    formatter: Formatter = Formatter
    parser: Parser = Parser
    parse_method: str
    db: DB = DB
    updater: Updater = Updater
    calendar_serializer = CalendarSerializer()

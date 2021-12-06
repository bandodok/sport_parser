from sport_parser.api.serializers import CalendarSerializer
from sport_parser.khl.models import ModelList
from sport_parser.khl.objects import Season, Team, Match
from sport_parser.khl.data_analysis.chart_stats import ChartStats
from sport_parser.khl.data_analysis.table_stats import TableStats
from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.data_taking.parser import Parser
from sport_parser.khl.data_taking.db import DB
from sport_parser.khl.updater import Updater


class Creator:
    def __init__(self, request):
        app_name = request.app_name
        if app_name == 'khl':
            self.config = Config
        else:
            raise AttributeError('no config selected')

    def get_season_class(self, season_id):
        return self.config.season_class(season_id, config=self.config)

    def get_team_class(self, team_id):
        return self.config.team_class(team_id, config=self.config)

    def get_match_class(self, match_id):
        return self.config.match_class(match_id, config=self.config)

    def get_updater(self):
        return self.config.updater(config=self.config)

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


class Config:
    title = 'КХЛ'
    league_title = 'Континентальная хоккейная лига'
    league_logo = 'KHL.webp'
    background_image = 'tribuna.webp'
    theme = 'khlTheme.css'

    models = ModelList()
    season_class = Season
    team_class = Team
    match_class = Match
    TableStats = TableStats
    ChartStats = ChartStats
    formatter = Formatter
    parser = Parser
    db = DB
    updater = Updater
    table_stats_names = {
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
    table_stats = {
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
    chart_stats_names = {
        'sh': ('Sh', 'int'),
        'sog': ('Sog', 'int'),
        'g': ('G', 'int'),
        'blocks': ('Blocks', 'int'),
        'penalty': ('Penalty', 'int'),
        'hits': ('Hits', 'int'),
        'time_a': ('TimeA', 'time'),
    }
    updated_team_names = {
        'Торпедо НН': 'Торпедо',
        'Динамо Мск': 'Динамо М',
        'ХК Динамо М': 'Динамо М',
        'ХК Сочи': 'Сочи'
    }
    updater_ignore = ['872325', '872404', '872667']
    calendar_serializer = CalendarSerializer()

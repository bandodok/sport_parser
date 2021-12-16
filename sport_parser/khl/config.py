from sport_parser.api.serializers import CalendarSerializer
from sport_parser.khl.models import ModelList
from sport_parser.khl.objects import Season, Team, Match
from sport_parser.khl.data_analysis.chart_stats import ChartStats
from sport_parser.khl.data_analysis.table_stats import TableStats
from sport_parser.khl.data_analysis.bar_stats import BarStats
from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.data_taking.parser import Parser
from sport_parser.khl.data_taking.db import DB
from sport_parser.khl.updater import Updater


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
    BarStats = BarStats
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
    bar_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'time_a': ('TimeA', 'Время в атаке', 'time'),
    }
    chart_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'time_a': ('TimeA', 'Время в атаке', 'time'),
    }
    updated_team_names = {
        'Торпедо НН': 'Торпедо',
        'Динамо Мск': 'Динамо М',
        'ХК Динамо М': 'Динамо М',
        'ХК Сочи': 'Сочи'
    }
    updater_ignore = ['872325', '872404', '872667']
    calendar_serializer = CalendarSerializer()

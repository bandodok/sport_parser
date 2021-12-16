from sport_parser.khl.config import Config

from sport_parser.nhl.models import ModelList
from sport_parser.nhl.parser import NHLParser

from sport_parser.khl.objects import Team


class NHLConfig(Config):
    title = 'НХЛ'
    league_title = 'Национальная хоккейная лига'
    league_logo = 'NHL.webp'
    background_image = 'tribuna.webp'  # заменить
    theme = 'khlTheme.css'  # заменить

    team_class = Team

    models = ModelList
    parser = NHLParser
    table_stats_names = {
        'sog': ('SoG', 'int'),
        'sog__a': ('SoG(A)', 'int'),
        'g': ('G', 'int'),
        'g__a': ('G(A)', 'int'),
        'faceoff_p': ('FaceOff%', 'percent'),
        'hits': ('Hits', 'int'),
        'blocks': ('Blocks', 'int'),
        'blocks__a': ('Blocks(A)', 'int'),
        'blocks__e': ('Blocks%', 'percent'),
        'penalty': ('Penalty', 'int'),
        'ppp': ('PowerPlay%', 'percent'),
        'ppg': ('PowerPlayGoals', 'int'),
        'takeaways': ('Takeaways', 'int'),
        'giveaways': ('Giveaways', 'int'),
    }
    table_stats = {
        'sog': 'median',
        'g': 'median',
        'hits': 'median',
        'blocks': 'median',
        'penalty': 'median',
        'ppp': 'median',
        'ppg': 'median',
        'takeaways': 'median',
        'giveaways': 'median',
        'faceoff_p': 'median',

        'sog__a': 'median',
        'g__a': 'median',
        'blocks__a': 'median',

        'blocks__e': 'blocks / (blocks + blocks__a) * 100',
    }
    bar_stats_names = {
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'ppp': ('PowerPlay%', 'Время игры в большинстве', 'percent'),
        'ppg': ('PowerPlayGoals', 'Голы в большинстве', 'int'),
        'takeaways': ('Takeaways', 'Отборы', 'int'),
        'giveaways': ('Giveaways', 'Потери', 'int'),
    }
    chart_stats_names = {
        'sog': ('Sog', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'ppg': ('PowerPlayGoals', 'Голы в большинстве', 'int'),
        'takeaways': ('Takeaways', 'Отборы', 'int'),
        'giveaways': ('Giveaways', 'Потери', 'int'),
    }

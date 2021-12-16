from sport_parser.khl.config import Config

from sport_parser.nhl.models import ModelList
from sport_parser.nhl.parser import NHLParser


class NHLConfig(Config):
    title = 'НХЛ'
    league_title = 'Национальная хоккейная лига'
    league_logo = 'NHL.webp'
    background_image = 'tribuna.webp'  # заменить
    theme = 'nhlTheme.css'  # заменить
    models = ModelList
    parser = NHLParser
    table_stats_names = {
        'sh': ('Sh', 'int'),
        'sh__a': ('Sh(A)', 'int'),
        'sh__e': ('Sh%', 'percent'),
        'sog': ('SoG', 'int'),
        'sog__a': ('SoG(A)', 'int'),
        'sog__e': ('AQ', 'percent'),
        'g': ('G', 'int'),
        'g__a': ('G(A)', 'int'),
        'faceoff_p': ('FaceOff%', 'percent'),
        'dev__e': ('DEV%', 'percent'),
        'pdo__e': ('PDO%', 'percent'),
        'hits': ('Hits', 'int'),
        'blocks': ('Blocks', 'int'),
        'blocks__a': ('Blocks(A)', 'int'),
        'blocks__e': ('Blocks%', 'percent'),
        'penalty': ('Penalty', 'int'),
        'ppg': ('PPG', 'int'),
        'takeaways': ('TA', 'int'),
        'giveaways': ('GA', 'int'),
    }
    table_stats = {
        'sh': 'median',
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

        'sh__a': 'median',
        'sog__a': 'median',
        'g__a': 'median',
        'blocks__a': 'median',

        'sh__e': 'sh / (sh + sh__a) * 100',
        'sog__e': 'sog / sh * 100',
        'blocks__e': 'blocks / (blocks + blocks__a) * 100',
        'dev__e': '(1 - (sog__a / sh__a)) * 100',
        'pdo__e': '((sh / (sh + sh__a)) + (sog / sh)) * 100',
    }
    bar_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'ppg': ('PPG', 'Голы в большинстве', 'int'),
        'takeaways': ('TA', 'Отборы', 'int'),
        'giveaways': ('GA', 'Потери', 'int'),
    }
    chart_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('Sog', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'ppg': ('PPG', 'Голы в большинстве', 'int'),
        'takeaways': ('TA', 'Отборы', 'int'),
        'giveaways': ('GA', 'Потери', 'int'),
    }

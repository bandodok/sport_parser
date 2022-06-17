from sport_parser.core.config import Config

from sport_parser.nhl.models import NHLModelList
from sport_parser.nhl.parser import NHLParser


class NHLConfig(Config):
    name = 'nhl'
    title = 'НХЛ'
    league_title = 'Национальная хоккейная лига'
    league_logo = 'NHL.webp'
    background_image = 'tribuna.webp'
    theme = 'nhlTheme.css'
    models = NHLModelList
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
        'takeaways': ('TA', 'int'),
        'giveaways': ('GA', 'int'),
    }
    table_stats_types = {
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
        'pdo__e': 'sog__e + dev__e',
    }
    bar_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'takeaways': ('TA', 'Отборы', 'int'),
        'giveaways': ('GA', 'Потери', 'int'),
    }
    live_bar_stats_names = {
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
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
    glossary = {
        'Sh': {'short': 'Все броски',
               'long': 'Все броски команды в сторону ворот соперника, включая броски в створ, промахи,'
                       ' блокированные броски и голы'},
        'Sh(A)': {'short': 'Все броски соперника',
                  'long': 'Все броски команды соперника в сторону ворот, включая броски в створ, промахи,'
                          ' блокированные броски и голы'},
        'Sh%': {'short': 'Процент бросков',
                'long': 'Процент всех бросков команды от общего количества <br>'
                        'Sh% = (Sh / (Sh + Sh(A))) * 100'},
        'SoG': {'short': 'Броски в створ', 'long': ''},
        'SoG(A)': {'short': 'Броски в створ соперника', 'long': ''},
        'AQ': {'short': 'Качество атаки',
               'long': 'Показывает, какая часть бросков доходит до створа ворот соперника <br>'
                       'AQ = (SoG / (Sh + Sh(A))) * 100'},
        'G': {'short': 'Голы', 'long': ''},
        'G(A)': {'short': 'Голы соперника', 'long': ''},
        'FaceOff%': {'short': 'Выигранные вбрасывания', 'long': ''},
        'DEV%': {'short': 'Разрушение атак соперника',
                 'long': 'Показывает, какая часть бросков соперника блокируется или идет мимо <br>'
                         'DEV% = (1 - (SoG(A) / Sh(A))) * 100'},
        'PDO%': {'short': 'Оборона + атака', 'long': 'Сумма показателей качества атаки и разрушения атак соперника'},
        'Hits': {'short': 'Силовые приемы', 'long': ''},
        'Blocks': {'short': 'Блокированные броски', 'long': ''},
        'Blocks(A)': {'short': 'Блокированные броски соперника', 'long': ''},
        'Blocks%': {'short': 'Процент блокированных бросков', 'long': ''},
        'Penalty': {'short': 'Удаления', 'long': ''},
        'TA': {'short': 'Отборы', 'long': ''},
        'GA': {'short': 'Потери', 'long': ''},
    }

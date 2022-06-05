from sport_parser.core.config import Config

from sport_parser.khl.models import KHLModelList
from sport_parser.khl.parser import KHLParser


class KHLConfig(Config):
    name = 'khl'
    title = 'КХЛ'
    league_title = 'Континентальная хоккейная лига'
    league_logo = 'KHL.webp'
    background_image = 'tribuna.webp'
    theme = 'khlTheme.css'
    models = KHLModelList
    parser = KHLParser
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
        'pdo__e': 'sog__e + dev__e',
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
        'sh': ('Sh', 'Все броски', 'int'),
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'time_a': ('TimeA', 'Время в атаке', 'time'),
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
    live_bar_stats_names = {
        'sog': ('SoG', 'Броски в створ', 'int'),
        'g': ('G', 'Голы', 'int'),
        'faceoff': ('FaceOff', 'Выигранные вбрасывания', 'int'),
        'hits': ('Hits', 'Силовые приемы', 'int'),
        'blocks': ('Blocks', 'Блокированные броски', 'int'),
        'penalty': ('Penalty', 'Штрафное время', 'int'),
        'time_a': ('TimeA', 'Время в атаке', 'time'),
    }
    updated_team_names = {
        'Торпедо НН': 'Торпедо',
        'Динамо Мск': 'Динамо М',
        'ХК Динамо М': 'Динамо М',
        'ХК Сочи': 'Сочи'
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
        'TimeA': {'short': 'Время в атаке', 'long': ''},
        'TimeA(A)': {'short': 'Время в атаке соперника', 'long': ''},
        'TimeA%': {'short': 'Процент времени в атаке', 'long': 'Процент времени в атаке команды от общего времени'},
        'DEV%': {'short': 'Разрушение атак соперника',
                 'long': 'Показывает, какая часть бросков соперника блокируется или идет мимо <br>'
                         'DEV% = (1 - (SoG(A) / Sh(A))) * 100'},
        'PDO%': {'short': 'Оборона + атака', 'long': 'Сумма показателей качества атаки и разрушения атак соперника'},
        'Hits': {'short': 'Силовые приемы', 'long': ''},
        'Blocks': {'short': 'Блокированные броски', 'long': ''},
        'Blocks(A)': {'short': 'Блокированные броски соперника', 'long': ''},
        'Blocks%': {'short': 'Процент блокированных бросков', 'long': ''},
        'Penalty': {'short': 'Удаления', 'long': ''},
    }
    updater_ignore = ['872325', '872404', '872667', '880834']


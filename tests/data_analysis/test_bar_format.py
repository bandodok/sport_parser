import pytest

from sport_parser.core.data_analysis.bar_stats import BarStats
from sport_parser.core.objects import Match
from sport_parser.core.config import Config

from sport_parser.khl.models import KHLTeams, KHLMatch


@pytest.mark.django_db(transaction=True)
def test_calculate(update_db):
    bs = BarStats(config=Config)
    team1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    _match = KHLMatch.objects.filter(teams=team1_id)[0]
    match = Match(_match.id, config=Config)
    bar_stats = bs.calculate(match)
    assert bar_stats == {
        'sh': {
            'short_title': 'Sh',
            'long_title': 'Все броски',
            'left_value': '44.0',
            'left_perc': 40,
            'right_value': '66.0',
            'right_perc': 60
        },
        'sog': {
            'short_title': 'SoG',
            'long_title': 'Броски в створ',
            'left_value': '22.0',
            'left_perc': 42,
            'right_value': '30.0',
            'right_perc': 57
        },
        'g': {
            'short_title': 'G',
            'long_title': 'Голы',
            'left_value': '4.0',
            'left_perc': 100,
            'right_value': '0.0',
            'right_perc': 0
        },
        'faceoff': {
            'short_title': 'FaceOff',
            'long_title': 'Выигранные вбрасывания',
            'left_value': '32.0',
            'left_perc': 55,
            'right_value': '26.0',
            'right_perc': 44
        }, 'hits': {
            'short_title': 'Hits',
            'long_title': 'Силовые приемы',
            'left_value': '16.0',
            'left_perc': 53,
            'right_value': '14.0',
            'right_perc': 46
        },
        'blocks': {
            'short_title': 'Blocks',
            'long_title': 'Блокированные броски',
            'left_value': '22.0',
            'left_perc': 61,
            'right_value': '14.0',
            'right_perc': 38
        }, 'penalty': {
            'short_title': 'Penalty',
            'long_title': 'Штрафное время',
            'left_value': '4.0',
            'left_perc': 25,
            'right_value': '12.0',
            'right_perc': 75
        }, 'time_a': {
            'short_title': 'TimeA',
            'long_title': 'Время в атаке',
            'left_value': '8:41',
            'left_perc': 44,
            'right_value': '10:37',
            'right_perc': 55
        }
    }


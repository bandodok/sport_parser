import pytest
from datetime import time

from sport_parser.khl.data_analysis.formatter import Formatter
from sport_parser.khl.objects import Season, Match, Team
from fixtures.db_fixture import update_db, get_teams, get_matches

from sport_parser.khl.models import KHLTeams, KHLMatch


def test_time_to_sec():
    f = Formatter()
    time1 = time(1, 30, 0)
    assert f.time_to_sec(time1) == 5400


def test_sec_to_time():
    f = Formatter()
    time1 = time(1, 30, 0)
    time2 = 5400
    assert f.sec_to_time(time1) == '90:00'
    assert f.sec_to_time(time2) == '90:00'


def test_chart_stat_format():
    f = Formatter()
    stat1 = 10
    stat2 = time(1, 30, 0)
    assert f.chart_stat_format(stat1) == 10
    assert f.chart_stat_format(stat2) == 5400


def test_table_stat_format():
    f = Formatter()
    stat_names = {
        'sh': ('Sh', 'int'),
        'sh__e': ('Sh%', 'percent'),
        'time_a': ('TimeA', 'time'),
    }
    stats = {
        'sh': 10,
        'sh__e': 50,
        'time_a': 5400,
    }

    assert f.table_stat_format(stats, stat_names) == {
        'sh': '10.0',
        'sh__e': '50.00%',
        'time_a': '90:00',
    }


def test_date_format():
    f = Formatter()
    date1 = '2 декабря 2021, чт'
    date2 = '22 декабря 2021, чт'
    assert f.date_format(date1) == '2021-12-02'
    assert f.date_format(date2) == '2021-12-22'

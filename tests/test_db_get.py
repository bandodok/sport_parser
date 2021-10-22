import pytest

import datetime
from fixtures.db_fixture import update_db

from sport_parser.khl.database_services.db_get import get_team_list, get_match_list, get_team_stat, get_opponent_stat, \
    get_median, time_to_sec, sec_to_time, output_format, get_team_name
from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_get_team_list(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    id2 = KHLTeams.objects.get(name='test2').id
    id3 = KHLTeams.objects.get(name='test6').id
    team_list = get_team_list(21)
    assert team_list == [id1, id2, id3]


@pytest.mark.django_db(transaction=True)
def test_get_match_list(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    match_list = get_match_list(id1)
    assert match_list == [15, 17, 19, 22]


@pytest.mark.django_db(transaction=True)
def test_get_team_stat(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    match_list = get_match_list(id1)
    out1 = get_team_stat(id1, 'g', match_list, mode='list')
    out2 = get_team_stat(id1, 'g', match_list, mode='median')
    out3 = get_team_stat(id1, 'g', match_list, mode='sum')
    assert out1 == [4, 8, 10, 1]
    assert out2 == 6
    assert out3 == 23


@pytest.mark.django_db(transaction=True)
def test_get_opponent_stat(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    match_list = get_match_list(id1)
    out1 = get_opponent_stat(id1, 'g', match_list, mode='list')
    out2 = get_opponent_stat(id1, 'g', match_list, mode='median')
    out3 = get_opponent_stat(id1, 'g', match_list, mode='sum')
    assert out1 == [0, 5, 8, 3]
    assert out2 == 4.0
    assert out3 == 16


def test_get_median():
    items1 = [1, 2, 3]
    items2 = ['1', '2', '3']
    items3 = [datetime.time(0, 1, 14), datetime.time(0, 1, 20), datetime.time(0, 2, 0)]
    out1 = get_median(items1)
    out2 = get_median(items2)
    out3 = get_median(items3)
    assert out1 == 2
    assert out2 == '2'
    assert out3 == 80


def test_time_to_sec():
    time = datetime.time(0, 1, 14)
    out = time_to_sec(time)
    assert out == 74


def test_sec_to_time():
    sec = 74
    out = sec_to_time(sec)
    assert out == '1:14'


def test_output_format():
    items = [1.234234, 2.654654, '12:12', 'foo']
    out = output_format(items)
    assert out == ['1.2', '2.7', '12:12', 'foo']


@pytest.mark.django_db(transaction=True)
def test_get_team_name(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    name = get_team_name(team_id)
    assert name == 'test1'

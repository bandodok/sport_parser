import pytest

import datetime

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database
from sport_parser.khl.database_services.db_get import get_team_list, get_match_list, get_team_stat, get_opponent_stat, \
    get_median, time_to_sec, sec_to_time, output_format, get_team_name
from sport_parser.khl.models import KHLTeams


@pytest.fixture()
def update_db():
    teams = [
        ['test1', 'img', 'city', 'arena', 'division', 'conference', 21],
        ['test2', 'img', 'city', 'arena', 'division', 'conference', 21],
        ['test3', 'img', 'city', 'arena', 'division', 'conference', 19],
        ['test4', 'img', 'city', 'arena', 'division', 'conference', 19],
        ['test5', 'img', 'city', 'arena', 'division', 'conference', 18],
        ['test6', 'img', 'city', 'arena', 'division', 'conference', 21]
    ]
    matches = [
        [15, '2017-08-21 19:30:00', 21, 'arena', 'city', 1],
        [16, '2017-08-21 19:30:00', 19, 'arena', 'city', 1],
        [17, '2017-08-21 19:30:00', 21, 'arena', 'city', 1],
    ]
    protocols = [
        [['test1', 15, '4', '22', '4', '32', '55.17', '22', '16', '5', '00:08:41', '00:16:38', '00:06:40',
          '66.31', '44'],
         ['test2', 15, 0, '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40', '68.97',
          '66']],
        [['test3', 16, '4', '22', '4', '32', '55.17', '22', '16', '5', '00:08:41', '00:16:38', '00:06:40',
          '66.31', '44'],
         ['test4', 16, 0, '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40', '68.97',
          '66']],
        [['test1', 17, '8', '22', '4', '32', '55.17', '22', '16', '5', '00:08:41', '00:16:38', '00:06:40',
          '66.31', '44'],
         ['test6', 17, '5', '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40', '68.97',
          '66']],
    ]
    for team in teams:
        add_teams_to_database(team)
    for match in matches:
        add_matches_to_database(match)
    for protocol in protocols:
        add_khl_protocol_to_database(protocol)


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
    assert match_list == [15, 17]


@pytest.mark.django_db(transaction=True)
def test_get_team_stat(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    match_list = get_match_list(id1)
    out1 = get_team_stat(id1, 'g', match_list, mode='list')
    out2 = get_team_stat(id1, 'g', match_list, mode='median')
    out3 = get_team_stat(id1, 'g', match_list, mode='sum')
    assert out1 == [4, 8]
    assert out2 == 6
    assert out3 == 12


@pytest.mark.django_db(transaction=True)
def test_get_opponent_stat(update_db):
    id1 = KHLTeams.objects.get(name='test1').id
    match_list = get_match_list(id1)
    out1 = get_opponent_stat(id1, 'g', match_list, mode='list')
    out2 = get_opponent_stat(id1, 'g', match_list, mode='median')
    out3 = get_opponent_stat(id1, 'g', match_list, mode='sum')
    assert out1 == [0, 5]
    assert out2 == 2.5
    assert out3 == 5


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

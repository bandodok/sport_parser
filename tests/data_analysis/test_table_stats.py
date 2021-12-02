import pytest
from datetime import time

from sport_parser.khl.data_analysis.table_stats import TableStats
from sport_parser.khl.objects import Season
from fixtures.db_fixture import update_db, get_teams, get_matches

from sport_parser.khl.models import KHLTeams, KHLMatch


@pytest.mark.django_db(transaction=True)
def test_season_stats_calculate(update_db):
    ts = TableStats()

    s = Season(21)
    test1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    test2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    test6_id = KHLTeams.objects.get(name='test6', season_id=21).id

    match_list = s.get_match_list()
    team_list = s.get_team_list()
    protocol_list = s.get_protocol_list()
    stats = ts.season_stats_calculate(match_list, team_list, protocol_list)
    assert stats == [
        ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA',
         'TimeA(A)', 'TimeA%', 'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
        [test1_id, 'test1', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
        [test2_id, 'test2', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.5', '6.5', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
        [test6_id, 'test6', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.0', '5.5', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']
    ]


@pytest.mark.django_db(transaction=True)
def test_match_stats_calculate(update_db):
    ts = TableStats()

    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    match = KHLMatch.objects.filter(teams=team1_id)[0]
    stats = ts.match_stats_calculate(match)
    assert stats == [
        ['Team', 'Sh', 'SoG', 'G', 'FaceOff', 'FaceOff%', 'Hits', 'Blocks', 'Penalty', 'TimeA'],
        [team1_id, 'test1', '44.0', '22.0', '4.0', '32.0', '55.17%', '16.0', '22.0', '4.0', '8:41'],
        [team2_id, 'test2', '66.0', '30.0', '0.0', '26.0', '44.83%', '14.0', '14.0', '12.0', '10:37']
    ]


@pytest.mark.django_db(transaction=True)
def test_get_team_match_stats(update_db):
    ts = TableStats()

    team = KHLTeams.objects.get(name='test1')
    match = KHLMatch.objects.filter(teams=team.id)[0]
    stats = ts.get_team_match_stats(team, match)
    assert stats == ['44.0', '22.0', '4.0', '32.0', '55.17%', '16.0', '22.0', '4.0', '8:41']


@pytest.mark.django_db(transaction=True)
def test_get_team_season_stats(update_db):
    ts = TableStats()

    s = Season(21)
    team = KHLTeams.objects.get(name='test1', season_id=21)
    match_list = s.get_match_list()
    protocol_list = s.get_protocol_list()
    ts.protocol_list = protocol_list
    ts._parse_stats()
    stats = ts.get_team_season_stats(team, match_list)
    assert stats == ['55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%', '9:39',
                     '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']


@pytest.mark.django_db(transaction=True)
def test_get_team_stat(update_db):
    ts = TableStats()

    s = Season(21)
    team = KHLTeams.objects.get(name='test1', season_id=21)
    match_list = s.get_match_list()
    protocol_list = s.get_protocol_list()
    ts.protocol_list = protocol_list
    ts._parse_stats()

    stat_list = ['sh', 'sog', 'g', 'time_a', 'hits', 'faceoff']
    mode_list = ['median', 'median', 'median', 'median', 'median', 'sum']
    stats = [55, 26, 6, 579, 15, 116]

    for stat, mode, team_stat in zip(stat_list, mode_list, stats):
        assert team_stat == ts.get_team_stat(team, stat, match_list, mode=mode)


@pytest.mark.django_db(transaction=True)
def test_get_opponent_stat(update_db):
    ts = TableStats()

    s = Season(21)
    team = KHLTeams.objects.get(name='test1', season_id=21)
    match_list = s.get_match_list()
    protocol_list = s.get_protocol_list()
    ts.protocol_list = protocol_list
    ts._parse_stats()

    stat_list = ['sh', 'sog', 'g', 'time_a', 'hits', 'faceoff']
    mode_list = ['median', 'median', 'median', 'median', 'median', 'sum']
    stats = [55, 26, 5, 579, 15, 232]

    for stat, mode, team_stat in zip(stat_list, mode_list, stats):
        assert team_stat == ts.get_opponent_stat(team, stat, match_list, mode=mode)


def test_get_median():
    ts = TableStats()
    items1 = [1, 2, 3, 4, 5]
    items2 = [1, 2, 3, 4, 5, 6]

    time1 = time(1, 15, 0)
    time2 = time(1, 45, 0)
    items3 = [time1, time2]

    assert ts.get_median(items1) == 3
    assert ts.get_median(items2) == 3.5
    assert ts.get_median(items3) == 5400

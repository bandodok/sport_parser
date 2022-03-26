import pytest
from datetime import datetime, timezone
from freezegun import freeze_time

from sport_parser.core.data_taking.db import DB
from sport_parser.core.objects import Season
from sport_parser.core.config import Config

from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_get_match_list(update_db):
    s = Season(21, config=Config)
    match_list = s.get_match_list()
    assert len(match_list) == 12
    for match in match_list:
        assert match.season_id == 21


@pytest.mark.django_db(transaction=True)
def test_get_team_list(update_db):
    s = Season(21, config=Config)
    team_list = s.get_team_list()
    assert [team.name for team in team_list] == ['test1', 'test2', 'test6']


@pytest.mark.django_db(transaction=True)
def test_get_protocol_list(update_db):
    s = Season(21, config=Config)
    protocol_list = s.get_protocol_list()
    assert len(protocol_list) == 12
    for protocol in protocol_list:
        assert protocol.team.season_id == 21


@pytest.mark.django_db(transaction=True)
def test_get_last_matches(update_db):
    s = Season(21, config=Config)
    match_list = s.get_last_matches(5)
    assert len(match_list) == 5
    for match in match_list:
        assert match.season_id == 21


@pytest.mark.django_db(transaction=True)
def test_get_future_matches(update_db):
    s = Season(21, config=Config)
    match_list = s.get_future_matches(5)
    assert len(match_list) == 5
    for match in match_list:
        assert match.season_id == 21


@pytest.mark.django_db(transaction=True)
def test_last_updated(get_teams, get_matches):
    db = DB(config=Config)
    s = Season(21, config=Config)
    with freeze_time(datetime(2012, 1, 14, tzinfo=timezone.utc)):
        db.add_team(get_teams[0])
        db.add_team(get_teams[1])
        for match in get_matches:
            db.add_match(match)
    with freeze_time(datetime(2018, 4, 24, tzinfo=timezone.utc)):
        update = s.last_updated()
        assert update == datetime(2012, 1, 14, tzinfo=timezone.utc)
        s.last_updated(update=True)
        update = s.last_updated()
        assert update == datetime(2018, 4, 24, tzinfo=timezone.utc)


@pytest.mark.django_db(transaction=True)
def test_get_stat_fields_list(update_db):
    s = Season(21, config=Config)
    fields = s.get_stat_fields_list()
    assert fields == ['g', 'g_1', 'g_2', 'g_3', 'g_ot', 'g_b', 'sh', 'sog', 'penalty', 'faceoff',
                      'faceoff_p', 'blocks', 'hits', 'fop', 'time_a', 'vvsh', 'nshv', 'pd']


@pytest.mark.django_db(transaction=True)
def test_get_table_stats(update_db):
    s = Season(21, config=Config)
    test1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    test2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    test6_id = KHLTeams.objects.get(name='test6', season_id=21).id
    stats = s.get_table_stats()
    assert stats == [['Team',  'Sh',  'Sh(A)',  'Sh%',  'SoG',  'SoG(A)',  'AQ',  'G',  'G(A)',
                      'FaceOff%',  'TimeA',  'TimeA(A)',  'TimeA%',  'DEV%',  'PDO%',  'Hits',
                      'Blocks',  'Blocks(A)',  'Blocks%',  'Penalty'],
                     [test1_id,  'test1',  '55.0',  '55.0',  '50.00%',  '26.0',  '26.0',  '47.27%',  '6.0',
                      '4.0',  '50.00%',  '9:39',  '9:39',  '50.00%',  '52.73%',  '97.27%',  '15.0',
                      '18.0',  '18.0',  '50.00%',  '8.0'],
                     [test2_id,  'test2',  '55.0',  '55.0',  '50.00%',  '26.0',  '26.0',  '47.27%',  '5.5',
                      '6.5',  '50.00%',  '9:39',  '9:39',  '50.00%',  '52.73%',  '97.27%',  '15.0',
                      '18.0',  '18.0',  '50.00%',  '8.0'],
                     [test6_id, 'test6', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.0', '5.5',
                      '50.00%', '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0',
                      '50.00%', '8.0']]

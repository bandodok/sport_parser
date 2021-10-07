from datetime import datetime, timezone
from freezegun import freeze_time

import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database, last_updated
from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch

ROW1 = {'team': 'test1', 'match_id': 12, 'g': '4', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17', 'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
        'pd': '66.31', 'sh': '44'}
ROW2 = {'team': 'test2', 'match_id': 12, 'g': 0, 'sog': '30', 'penalty': '12', 'faceoff': '26', 'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11', 'nshv': '00:06:40', 'pd': '68.97',
        'sh': '66'}
PROTOCOL = [ROW1, ROW2]
MATCH1 = {'match_id': 12, 'date': '2017-08-21', 'time': '15:00', 'season': 21, 'arena': 'arena', 'city': 'city',
          'finished': True, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
MATCH2 = {'match_id': 13, 'date': '2017-08-22', 'time': '15:01', 'season': 21, 'arena': 'arena', 'city': 'city',
          'finished': True, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
MATCH3 = {'match_id': 14, 'date': '2017-08-23', 'time': '15:02', 'season': 21, 'arena': 'arena', 'city': 'city',
          'finished': False, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
MATCHES = [MATCH1, MATCH2, MATCH3]
TEAM1 = ['test1', 'img', 'city', 'arena', 'division', 'conference', 21]
TEAM2 = ['test2', 'img', 'city', 'arena', 'division', 'conference', 21]


@pytest.mark.django_db(transaction=True)
def test_add_teams_to_database():
    add_teams_to_database(TEAM1)
    team = KHLTeams.objects.get(name='test1')
    assert team.id == 1
    assert team.img == 'img'
    assert team.city == 'city'
    assert team.arena == 'arena'
    assert team.division == 'division'
    assert team.conference == 'conference'
    assert team.season == 21


@pytest.mark.django_db(transaction=True)
def test_add_matches_to_database():
    add_teams_to_database(TEAM1)
    add_teams_to_database(TEAM2)
    add_matches_to_database(MATCHES)
    match = KHLMatch.objects.get(match_id=12)
    assert match.season == 21
    assert match.arena == 'arena'
    assert match.city == 'city'


@pytest.mark.django_db(transaction=True)
def test_add_khl_protocol_to_database():
    add_teams_to_database(TEAM1)
    add_teams_to_database(TEAM2)
    add_matches_to_database(MATCHES)
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    add_khl_protocol_to_database(PROTOCOL)
    team1 = KHLProtocol.objects.get(team_id=team1_id)
    team2 = KHLProtocol.objects.get(team_id=team2_id)
    assert team1.g == 4
    assert team2.g == 0
    assert team1.sh == 44
    assert team2.sh == 66
    assert team1.sog == 22
    assert team2.sog == 30


@pytest.mark.django_db(transaction=True)
def test_last_updated():
    with freeze_time(datetime(2012, 1, 14, tzinfo=timezone.utc)):
        add_teams_to_database(TEAM1)
        add_teams_to_database(TEAM2)
        add_matches_to_database(MATCHES)
    with freeze_time(datetime(2018, 4, 24, tzinfo=timezone.utc)):
        update = last_updated()
        assert update == datetime(2012, 1, 14, tzinfo=timezone.utc)
        last_updated(update=True)
        update = last_updated()
        assert update == datetime(2018, 4, 24, tzinfo=timezone.utc)

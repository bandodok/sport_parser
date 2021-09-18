from datetime import datetime, timezone
from freezegun import freeze_time

import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database, last_updated
from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch

ROW1 = ['test1', 12, '4', '22', '4', '32', '55.17', '22', '16', '5', '00:08:41', '00:16:38', '00:06:40',
        '66.31', '44']
ROW2 = ['test2', 12, 0, '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40', '68.97',
        '66']
PROTOCOL = [ROW1, ROW2]
MATCH = [12, '2017-08-21 19:30:00', 21, 'arena', 'city', 1]
TEAM1 = ['test1', 'img', 'city', 'arena', 'division', 'conference', 21]
TEAM2 = ['test2', 'img', 'city', 'arena', 'division', 'conference', 21]


@pytest.mark.django_db(transaction=True)
def test_add_matches_to_database():
    add_matches_to_database(MATCH)
    match = KHLMatch.objects.get(match_id=12)
    assert match.season == 21
    assert match.arena == 'arena'
    assert match.city == 'city'
    assert match.viewers == 1


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
def test_add_khl_protocol_to_database():
    add_matches_to_database(MATCH)
    add_teams_to_database(TEAM1)
    add_teams_to_database(TEAM2)
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
        add_matches_to_database(MATCH)
    with freeze_time(datetime(2018, 4, 24, tzinfo=timezone.utc)):
        update = last_updated()
        assert update == datetime(2012, 1, 14, tzinfo=timezone.utc)
        last_updated(update=True)
        update = last_updated()
        assert update == datetime(2018, 4, 24, tzinfo=timezone.utc)

from datetime import datetime, timezone
from freezegun import freeze_time

import pytest

from fixtures.db_fixture import get_protocol, get_teams, get_matches
from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database, last_updated
from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch


@pytest.mark.django_db(transaction=True)
def test_add_teams_to_database(get_teams):
    add_teams_to_database(get_teams[0])
    team = KHLTeams.objects.get(name='test1')
    assert team.img == 'img'
    assert team.city == 'city'
    assert team.arena == 'arena'
    assert team.division == 'division'
    assert team.conference == 'conference'
    assert team.season == 21


@pytest.mark.django_db(transaction=True)
def test_add_matches_to_database(get_teams, get_matches):
    add_teams_to_database(get_teams[0])
    add_teams_to_database(get_teams[1])
    add_matches_to_database(get_matches)
    match = KHLMatch.objects.get(match_id=12)
    assert match.season == 21
    assert match.arena == 'arena'
    assert match.city == 'city'


@pytest.mark.django_db(transaction=True)
def test_add_khl_protocol_to_database(get_teams, get_matches, get_protocol):
    add_teams_to_database(get_teams[0])
    add_teams_to_database(get_teams[1])
    add_matches_to_database(get_matches)
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    add_khl_protocol_to_database(get_protocol)
    team1 = KHLProtocol.objects.get(team_id=team1_id)
    team2 = KHLProtocol.objects.get(team_id=team2_id)
    assert team1.g == 4
    assert team2.g == 0
    assert team1.sh == 44
    assert team2.sh == 66
    assert team1.sog == 22
    assert team2.sog == 30


@pytest.mark.django_db(transaction=True)
def test_last_updated(get_teams, get_matches):
    with freeze_time(datetime(2012, 1, 14, tzinfo=timezone.utc)):
        add_teams_to_database(get_teams[0])
        add_teams_to_database(get_teams[1])
        add_matches_to_database(get_matches)
    with freeze_time(datetime(2018, 4, 24, tzinfo=timezone.utc)):
        update = last_updated()
        assert update == datetime(2012, 1, 14, tzinfo=timezone.utc)
        last_updated(update=True)
        update = last_updated()
        assert update == datetime(2018, 4, 24, tzinfo=timezone.utc)

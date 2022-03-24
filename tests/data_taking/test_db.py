import pytest

from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch
from sport_parser.core.data_taking.db import DB
from sport_parser.core.config import Config


@pytest.mark.django_db(transaction=True)
def test_add_team(get_teams):
    db = DB(config=Config)
    db.add_team(get_teams[0])
    team = KHLTeams.objects.get(name='test1')
    assert team.img == 'img'
    assert team.city == 'city'
    assert team.arena == 'arena'
    assert team.division == 'division'
    assert team.conference == 'conference'
    assert team.season.id == 21


@pytest.mark.django_db(transaction=True)
def test_add_match(get_teams, get_matches):
    db = DB(config=Config)
    db.add_team(get_teams[0])
    db.add_team(get_teams[1])
    for match in get_matches:
        db.add_match(match)
    match = KHLMatch.objects.get(id=12)
    assert match.season.id == 21
    assert match.arena == 'arena'
    assert match.city == 'city'


@pytest.mark.django_db(transaction=True)
def test_add_protocol(get_teams, get_matches, get_protocol):
    db = DB(config=Config)
    db.add_team(get_teams[0])
    db.add_team(get_teams[1])
    for match in get_matches:
        db.add_match(match)
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    db.add_protocol(get_protocol)
    team1 = KHLProtocol.objects.get(team=team1_id)
    team2 = KHLProtocol.objects.get(team=team2_id)
    assert team1.g == 4
    assert team2.g == 0
    assert team1.sh == 44
    assert team2.sh == 66
    assert team1.sog == 22
    assert team2.sog == 30

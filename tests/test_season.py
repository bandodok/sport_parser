import pytest
from datetime import datetime, timezone
from freezegun import freeze_time

from sport_parser.khl.objects import Season
from sport_parser.khl.models import KHLSeason
from fixtures.db_fixture import update_db

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database, last_updated

from fixtures.db_fixture import get_protocol, get_teams, get_matches

from sport_parser.khl.database_services.db_get import get_team_list, get_match_list, get_team_stat, get_opponent_stat, \
    get_median, time_to_sec, sec_to_time, output_format, get_team_name
from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_season_get_match_list(update_db):
    s = Season(KHLSeason, 21)
    match_list = s.get_match_list()
    assert [match.id for match in match_list] == [15, 17, 18, 19, 20, 22, 23, 25, 26, 27, 28, 30]


@pytest.mark.django_db(transaction=True)
def test_season_get_team_list(update_db):
    s = Season(KHLSeason, 21)
    team_list = s.get_team_list()
    assert [team.name for team in team_list] == ['test1', 'test2', 'test6']


@pytest.mark.django_db(transaction=True)
def test_season_get_last_matches(update_db):
    s = Season(KHLSeason, 21)
    match_list = s.get_last_matches(5)
    assert [match.id for match in match_list] == [22, 20, 19, 18, 17]


@pytest.mark.django_db(transaction=True)
def test_season_get_future_matches(update_db):
    s = Season(KHLSeason, 21)
    match_list = s.get_future_matches(5)
    assert [match.id for match in match_list] == [23, 25, 26, 27, 28]


@pytest.mark.django_db(transaction=True)
def test_season_last_updated(get_teams, get_matches):
    KHLSeason.objects.create(id=21, external_id=1097)
    s = Season(KHLSeason, 21)
    with freeze_time(datetime(2012, 1, 14, tzinfo=timezone.utc)):
        add_teams_to_database(get_teams[0])
        add_teams_to_database(get_teams[1])
        add_matches_to_database(get_matches)
    with freeze_time(datetime(2018, 4, 24, tzinfo=timezone.utc)):
        update = s.last_updated()
        assert update == datetime(2012, 1, 14, tzinfo=timezone.utc)
        s.last_updated(update=True)
        update = s.last_updated()
        assert update == datetime(2018, 4, 24, tzinfo=timezone.utc)

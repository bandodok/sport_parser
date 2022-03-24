import pytest

from sport_parser.core.objects import Team
from sport_parser.core.config import Config

from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_get_match_list(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)
    team = t.data
    match_list = t.get_match_list()
    assert len(match_list) == 8
    for match in match_list:
        assert team in match.teams.all()


@pytest.mark.django_db(transaction=True)
def test_get_self_protocol_list(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)
    team = t.data
    protocol_list = t.get_self_protocol_list()
    assert len(protocol_list) == 4
    for protocol in protocol_list:
        assert team == protocol.team


@pytest.mark.django_db(transaction=True)
def test_get_opponent_protocol_list(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)
    team = t.data
    protocol_list = t.get_self_protocol_list()
    assert len(protocol_list) == 4
    for protocol in protocol_list:
        assert team == protocol.team


@pytest.mark.django_db(transaction=True)
def test_get_last_matches(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)
    team = t.data
    match_list = t.get_last_matches(5)
    assert len(match_list) == 4
    for match in match_list:
        assert team in match.teams.all()


@pytest.mark.django_db(transaction=True)
def test_get_future_matches(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)
    team = t.data
    match_list = t.get_future_matches(5)
    assert len(match_list) == 4
    for match in match_list:
        assert team in match.teams.all()


@pytest.mark.django_db(transaction=True)
def test_get_table_stats(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)

    stats = t.get_table_stats()
    assert stats == [
        ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA',
         'TimeA(A)', 'TimeA%', 'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
        [team_id, 'test1', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']]


@pytest.mark.django_db(transaction=True)
def test_get_chart_stats(update_db):
    team_id = KHLTeams.objects.get(name='test1').id
    t = Team(team_id, config=Config)

    stats = t.get_chart_stats()
    assert stats == [
        ['Sh', 'Sog', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA', 'Sh(A)',
         'Sog(A)', 'G(A)', 'Blocks(A)', 'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
        [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
        [44, 22, 8, 22, 4, 16, 521, 66, 30, 5, 14, 12, 14, 637],
        [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 1, 14, 12, 14, 637, 44, 22, 3, 22, 4, 16, 521]]


@pytest.mark.django_db(transaction=True)
def test_get_another_season_team_ids(update_db):
    test2_18_id = KHLTeams.objects.get(name='test2', season_id=18).id
    test2_19_id = KHLTeams.objects.get(name='test2', season_id=19).id
    test2_21_id = KHLTeams.objects.get(name='test2', season_id=21).id
    t = Team(test2_21_id, config=Config)
    id_list = t.get_another_season_team_ids()
    assert id_list == [
        {'season': 18, 'id': test2_18_id},
        {'season': 19, 'id': test2_19_id},
        {'season': 21, 'id': test2_21_id}
    ]

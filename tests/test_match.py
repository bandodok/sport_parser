import pytest
import json

from sport_parser.khl.objects import Match
from sport_parser.khl.models import KHLMatch
from fixtures.db_fixture import update_db

from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_get_team1_score(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    score = m.get_team1_score()
    assert score == 4


@pytest.mark.django_db(transaction=True)
def test_get_team2_score(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    score = m.get_team2_score()
    assert score == 0


@pytest.mark.django_db(transaction=True)
def test_get_team1_score_by_period(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    score = m.get_team1_score_by_period()
    assert score == {
        'match': 4,
        'p1': 0,
        'p2': 0,
        'p3': 0,
        'ot': 0,
        'b': 0
    }


@pytest.mark.django_db(transaction=True)
def test_get_team2_score_by_period(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    score = m.get_team2_score_by_period()
    assert score == {
        'match': 0,
        'p1': 0,
        'p2': 0,
        'p3': 0,
        'ot': 0,
        'b': 0
    }


@pytest.mark.django_db(transaction=True)
def test_get_team1_last_matches(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team1 = m.team1
    match_list_json = m.get_team1_last_matches(5)
    match_list = json.loads(match_list_json)
    assert len(match_list) == 3
    for match in match_list.values():
        assert team1.data.id in match.values()


@pytest.mark.django_db(transaction=True)
def test_get_team2_last_matches(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team2 = m.team2
    match_list_json = m.get_team2_last_matches(5)
    match_list = json.loads(match_list_json)
    assert len(match_list) == 3
    for match in match_list.values():
        assert team2.data.id in match.values()


@pytest.mark.django_db(transaction=True)
def test_get_team1_future_matches(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team1 = m.team1
    match_list_json = m.get_team1_future_matches(5)
    match_list = json.loads(match_list_json)
    assert len(match_list) == 4
    for match in match_list.values():
        assert team1.data.id in match.values()


@pytest.mark.django_db(transaction=True)
def test_get_team2_future_matches(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team2 = m.team2
    match_list_json = m.get_team2_future_matches(5)
    match_list = json.loads(match_list_json)
    assert len(match_list) == 4
    for match in match_list.values():
        assert team2.data.id in match.values()


@pytest.mark.django_db(transaction=True)
def test_get_match_stats(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    stats = m.get_match_stats()
    assert stats == [
        ['Team', 'Sh', 'SoG', 'G', 'FaceOff', 'FaceOff%', 'Hits', 'Blocks', 'Penalty', 'TimeA'],
        [team1_id, 'test1', '44.0', '22.0', '4.0', '32.0', '55.17%', '16.0', '22.0', '4.0', '8:41'],
        [team2_id, 'test2', '66.0', '30.0', '0.0', '26.0', '44.83%', '14.0', '14.0', '12.0', '10:37']
    ]


@pytest.mark.django_db(transaction=True)
def test_get_table_stats(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    team2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    stats = m.get_table_stats()
    assert stats == [
        ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA',
         'TimeA(A)', 'TimeA%', 'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
        [team1_id, 'test1', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
        [team2_id, 'test2', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.5', '6.5', '50.00%',
         '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']
    ]


@pytest.mark.django_db(transaction=True)
def test_get_chart_stats(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    match_id = KHLMatch.objects.filter(teams=team1_id)[0].id
    m = Match(match_id)

    stats = m.get_chart_stats()
    assert stats == [
        ['test1', 'test1', 'test1', 'test1', 'test1', 'test1', 'test1',
         'test2', 'test2', 'test2', 'test2', 'test2', 'test2', 'test2'],
        [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
        [44, 22, 8, 22, 4, 16, 521, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 1, 14, 12, 14, 637, 66, 30, 3, 14, 12, 14, 637]
    ]

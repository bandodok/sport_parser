import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database
from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.team_stats import get_team_stats_view


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
         ['test6', 17, '1', '30', '12', '16', '34.04', '6', '14', '4', '00:09:47', '00:17:13', '00:06:37', '67.27',
          '52']],
    ]
    for team in teams:
        add_teams_to_database(team)
    for match in matches:
        add_matches_to_database(match)
    for protocol in protocols:
        add_khl_protocol_to_database(protocol)


@pytest.mark.django_db(transaction=True)
def test_get_team_stats_view(update_db):
    stats = [
        ['Sh', 'SoG', 'G', 'Blocks', 'Penalty', 'Hits',
         'Sh(A)', 'SoG(A)', 'G(A)', 'Blocks(A)', 'Penalty(A)', 'Hits(A)'],
        [44, 22, 4, 22, 4, 16, 66, 30, 0, 14, 12, 14],
        [44, 22, 8, 22, 4, 16, 52, 30, 1, 6, 12, 14]
    ]
    team1_id = KHLTeams.objects.get(name='test1').id
    out = get_team_stats_view(team1_id)
    assert out == stats

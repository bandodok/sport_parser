import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database
from sport_parser.khl.view_data.season_stats import get_season_stats_view


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
def test_get_season_stats_view(update_db):
    stats = [
        ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA', 'TimeA(A)', 'TimeA%',
         'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
        ['test1', '44.0', '59.0', '42.72%', '22.0', '30.0', '50.00%', '6.0', '0.5', '60.38%', '8:41', '10:12', '45.98%',
         '49.15%', '92.72%', '16.0', '22.0', '10.0', '68.75%', '4.0'],
        ['test2', '66.0', '44.0', '60.00%', '30.0', '22.0', '45.45%', '0.0', '4.0', '44.83%', '10:37', '8:41', '55.01%',
         '50.00%', '105.45%', '14.0', '14.0', '22.0', '38.89%', '12.0'],
        ['test6', '52.0', '44.0', '54.17%', '30.0', '22.0', '57.69%', '1.0', '8.0', '33.33%', '9:47', '8:41', '52.98%',
         '50.00%', '111.86%', '14.0', '6.0', '22.0', '21.43%', '12.0']
    ]
    out = get_season_stats_view(21)
    assert out == stats

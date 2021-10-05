from datetime import datetime, timezone

import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database


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
        {'match_id': 15, 'date': datetime(2017, 8, 20, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': False, 'viewers': 228,
         'home_team': 'test1', 'guest_team': 'test2'},
        {'match_id': 16, 'date': datetime(2017, 8, 22, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 19,
         'arena': 'arena', 'city': 'city', 'finished': False, 'viewers': 228,
         'home_team': 'test3', 'guest_team': 'test4'},
        {'match_id': 17, 'date': datetime(2017, 8, 23, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': False, 'viewers': 228,
         'home_team': 'test1', 'guest_team': 'test6'}
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
         ['test6', 17, '5', '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40', '68.97',
          '66']],
    ]
    for team in teams:
        add_teams_to_database(team)
    add_matches_to_database(matches)
    for protocol in protocols:
        add_khl_protocol_to_database(protocol)

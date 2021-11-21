from datetime import datetime, timezone

import pytest

from sport_parser.khl.database_services.db_add import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database
from sport_parser.khl.models import KHLSeason


@pytest.fixture()
def update_db():
    seasons = {
        '21': 1097,
        '20': 1045,
        '19': 851,
        '18': 671
    }
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
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test1', 'guest_team': 'test2'},
        {'match_id': 16, 'date': datetime(2017, 8, 22, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 19,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test3', 'guest_team': 'test4'},
        {'match_id': 17, 'date': datetime(2017, 8, 23, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test1', 'guest_team': 'test6'},
        {'match_id': 18, 'date': datetime(2017, 8, 24, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test2', 'guest_team': 'test6'},
        {'match_id': 19, 'date': datetime(2017, 8, 25, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test2', 'guest_team': 'test1'},
        {'match_id': 20, 'date': datetime(2017, 8, 26, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test6', 'guest_team': 'test2'},
        {'match_id': 21, 'date': datetime(2017, 8, 27, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 19,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test4', 'guest_team': 'test3'},
        {'match_id': 22, 'date': datetime(2017, 8, 28, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': 'arena', 'city': 'city', 'finished': True, 'viewers': 228,
         'home_team': 'test6', 'guest_team': 'test1'},

        {'match_id': 23, 'date': datetime(2017, 8, 29, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test1', 'guest_team': 'test2'},
        {'match_id': 24, 'date': datetime(2017, 8, 30, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 19,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test3', 'guest_team': 'test4'},
        {'match_id': 25, 'date': datetime(2017, 8, 31, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test1', 'guest_team': 'test6'},
        {'match_id': 26, 'date': datetime(2017, 9, 1, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test2', 'guest_team': 'test6'},
        {'match_id': 27, 'date': datetime(2017, 9, 2, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test2', 'guest_team': 'test1'},
        {'match_id': 28, 'date': datetime(2017, 9, 3, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test6', 'guest_team': 'test2'},
        {'match_id': 29, 'date': datetime(2017, 9, 4, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 19,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test4', 'guest_team': 'test3'},
        {'match_id': 30, 'date': datetime(2017, 9, 5, 21, 0, tzinfo=timezone.utc), 'time': '15:00', 'season': 21,
         'arena': '', 'city': 'city', 'finished': False, 'viewers': 0,
         'home_team': 'test6', 'guest_team': 'test1'},
    ]
    protocols = [
        [{'team': 'test1', 'match_id': 15, 'g': '4', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test2', 'match_id': 15, 'g': 0, 'sog': '30', 'penalty': '12', 'faceoff': '26', 'faceoff_p': '44.83',
          'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11', 'nshv': '00:06:40',
          'pd': '68.97', 'sh': '66'}],
        [{'team': 'test3', 'match_id': 16, 'g': '4', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test4', 'match_id': 16, 'g': 0, 'sog': '30', 'penalty': '12', 'faceoff': '26', 'faceoff_p': '44.83',
          'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11', 'nshv': '00:06:40',
          'pd': '68.97', 'sh': '66'}],
        [{'team': 'test1', 'match_id': 17, 'g': '8', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test6', 'match_id': 17, 'g': '5', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
        [{'team': 'test2', 'match_id': 18, 'g': '8', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test6', 'match_id': 18, 'g': '5', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
        [{'team': 'test2', 'match_id': 19, 'g': '8', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test1', 'match_id': 19, 'g': '10', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
        [{'team': 'test6', 'match_id': 20, 'g': '8', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test2', 'match_id': 20, 'g': '3', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
        [{'team': 'test4', 'match_id': 21, 'g': '7', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test3', 'match_id': 21, 'g': '5', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
        [{'team': 'test6', 'match_id': 22, 'g': '3', 'sog': '22', 'penalty': '4', 'faceoff': '32', 'faceoff_p': '55.17',
          'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
          'pd': '66.31', 'sh': '44'},
         {'team': 'test1', 'match_id': 22, 'g': '1', 'sog': '30', 'penalty': '12', 'faceoff': '26',
          'faceoff_p': '44.83', 'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11',
          'nshv': '00:06:40', 'pd': '68.97', 'sh': '66'}],
    ]
    for id, external_id in seasons.items():
        KHLSeason.objects.create(
            id=id,
            external_id=external_id
        )
    for team in teams:
        add_teams_to_database(team)
    add_matches_to_database(matches)
    for protocol in protocols:
        add_khl_protocol_to_database(protocol)


@pytest.fixture()
def get_protocol():
    row1 = {'team': 'test1', 'match_id': 12, 'g': '4', 'sog': '22', 'penalty': '4', 'faceoff': '32',
            'faceoff_p': '55.17',
            'blocks': '22', 'hits': '16', 'fop': '5', 'time_a': '00:08:41', 'vvsh': '00:16:38', 'nshv': '00:06:40',
            'pd': '66.31', 'sh': '44'}
    row2 = {'team': 'test2', 'match_id': 12, 'g': 0, 'sog': '30', 'penalty': '12', 'faceoff': '26',
            'faceoff_p': '44.83',
            'blocks': '14', 'hits': '14', 'fop': '1', 'time_a': '00:10:37', 'vvsh': '00:19:11', 'nshv': '00:06:40',
            'pd': '68.97', 'sh': '66'}
    return [row1, row2]


@pytest.fixture()
def get_matches():
    match1 = {'match_id': 12, 'date': '2017-08-21', 'time': '15:00', 'season': 21, 'arena': 'arena', 'city': 'city',
              'finished': True, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
    match2 = {'match_id': 13, 'date': '2017-08-22', 'time': '15:01', 'season': 21, 'arena': 'arena', 'city': 'city',
              'finished': True, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
    match3 = {'match_id': 14, 'date': '2017-08-23', 'time': '15:02', 'season': 21, 'arena': 'arena', 'city': 'city',
              'finished': False, 'viewers': 228, 'home_team': 'test1', 'guest_team': 'test2'}
    return [match1, match2, match3]


@pytest.fixture()
def get_teams():
    team1 = ['test1', 'img', 'city', 'arena', 'division', 'conference', 21]
    team2 = ['test2', 'img', 'city', 'arena', 'division', 'conference', 21]
    return team1, team2

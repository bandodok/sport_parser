from datetime import timezone
import datetime

import pytest
from fixtures.db_fixture import update_db

from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.team_stats import get_team_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_team_stats_view(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    team6_id = KHLTeams.objects.get(name='test6').id
    stats = {'arena': 'arena',
             'city': 'city',
             'conference': 'conference',
             'division': 'division',
             'team': 'test1',
             'logo': 'img',
             'season': 21,
             'seasons': [{'id': team1_id, 'season': 21}],
             'stats': [['Sh', 'SoG', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA',
                        'Sh(A)', 'SoG(A)', 'G(A)', 'Blocks(A)', 'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
                       [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
                       [44, 22, 8, 22, 4, 16, 521, 66, 30, 5, 14, 12, 14, 637],
                       [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
                       [66, 30, 1, 14, 12, 14, 637, 44, 22, 3, 22, 4, 16, 521]],
             'last_matches': '{"22/2017-08-28 21:00:00+00:00": {"date": '
                             '"2017-08-28T21:00:00Z", "time": "15:00:00", "id": 22, '
                             '"team1_name": "test6", "team1_score": 3, "team1_image": '
                             '"img", "team1_id": 61, "team2_name": "test1", "team2_score": '
                             '1, "team2_image": "img", "team2_id": 56}, "19/2017-08-25 '
                             '21:00:00+00:00": {"date": "2017-08-25T21:00:00Z", "time": '
                             '"15:00:00", "id": 19, "team1_name": "test2", "team1_score": '
                             '8, "team1_image": "img", "team1_id": 57, "team2_name": '
                             '"test1", "team2_score": 10, "team2_image": "img", '
                             '"team2_id": 56}, "17/2017-08-23 21:00:00+00:00": {"date": '
                             '"2017-08-23T21:00:00Z", "time": "15:00:00", "id": 17, '
                             '"team1_name": "test1", "team1_score": 8, "team1_image": '
                             '"img", "team1_id": 56, "team2_name": "test6", "team2_score": '
                             '5, "team2_image": "img", "team2_id": 61}, "15/2017-08-20 '
                             '21:00:00+00:00": {"date": "2017-08-20T21:00:00Z", "time": '
                             '"15:00:00", "id": 15, "team1_name": "test1", "team1_score": '
                             '4, "team1_image": "img", "team1_id": 56, "team2_name": '
                             '"test2", "team2_score": 0, "team2_image": "img", "team2_id": '
                             '57}}',
             'future_matches': '{"23/2017-08-29 21:00:00+00:00": {"date": '
                               '"2017-08-29T21:00:00Z", "time": "15:00:00", "id": 23, '
                               '"team1_name": "test1", "team1_image": "img", "team1_id": '
                               '56, "team2_name": "test2", "team2_image": "img", '
                               '"team2_id": 57}, "25/2017-08-31 21:00:00+00:00": {"date": '
                               '"2017-08-31T21:00:00Z", "time": "15:00:00", "id": 25, '
                               '"team1_name": "test1", "team1_image": "img", "team1_id": '
                               '56, "team2_name": "test6", "team2_image": "img", '
                               '"team2_id": 61}, "27/2017-09-02 21:00:00+00:00": {"date": '
                               '"2017-09-02T21:00:00Z", "time": "15:00:00", "id": 27, '
                               '"team1_name": "test1", "team1_image": "img", "team1_id": '
                               '56, "team2_name": "test2", "team2_image": "img", '
                               '"team2_id": 57}, "30/2017-09-05 21:00:00+00:00": {"date": '
                               '"2017-09-05T21:00:00Z", "time": "15:00:00", "id": 30, '
                               '"team1_name": "test1", "team1_image": "img", "team1_id": '
                               '56, "team2_name": "test6", "team2_image": "img", '
                               '"team2_id": 61}}',
             }
    team1_id = KHLTeams.objects.get(name='test1').id
    out = get_team_stats_view(team1_id)
    assert out == stats

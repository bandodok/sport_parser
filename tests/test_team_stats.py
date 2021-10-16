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
             'last_matches': {
                 15: {'date': datetime.datetime(2017, 8, 20, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team1_score': 4,
                      'team2_id': team2_id,
                      'team2_image': 'img',
                      'team2_name': 'test2',
                      'team2_score': 0,
                      'time': datetime.time(15, 0)},
                 17: {'date': datetime.datetime(2017, 8, 23, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team1_score': 8,
                      'team2_id': team6_id,
                      'team2_image': 'img',
                      'team2_name': 'test6',
                      'team2_score': 5,
                      'time': datetime.time(15, 0)},
                 19: {'date': datetime.datetime(2017, 8, 25, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team2_id,
                      'team1_image': 'img',
                      'team1_name': 'test2',
                      'team1_score': 8,
                      'team2_id': team1_id,
                      'team2_image': 'img',
                      'team2_name': 'test1',
                      'team2_score': 10,
                      'time': datetime.time(15, 0)},
                 22: {'date': datetime.datetime(2017, 8, 28, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team6_id,
                      'team1_image': 'img',
                      'team1_name': 'test6',
                      'team1_score': 3,
                      'team2_id': team1_id,
                      'team2_image': 'img',
                      'team2_name': 'test1',
                      'team2_score': 1,
                      'time': datetime.time(15, 0)}},
             'future_matches': {
                 23: {'date': datetime.datetime(2017, 8, 29, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team2_id': team2_id,
                      'team2_image': 'img',
                      'team2_name': 'test2',
                      'time': datetime.time(15, 0)},
                 25: {'date': datetime.datetime(2017, 8, 31, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team2_id': team6_id,
                      'team2_image': 'img',
                      'team2_name': 'test6',
                      'time': datetime.time(15, 0)},
                 27: {'date': datetime.datetime(2017, 9, 2, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team2_id': team2_id,
                      'team2_image': 'img',
                      'team2_name': 'test2',
                      'time': datetime.time(15, 0)},
                 30: {'date': datetime.datetime(2017, 9, 5, 21, 0, tzinfo=timezone.utc),
                      'team1_id': team1_id,
                      'team1_image': 'img',
                      'team1_name': 'test1',
                      'team2_id': team6_id,
                      'team2_image': 'img',
                      'team2_name': 'test6',
                      'time': datetime.time(15, 0)}
                 }
             }
    team1_id = KHLTeams.objects.get(name='test1').id
    out = get_team_stats_view(team1_id)
    assert out == stats

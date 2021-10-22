from datetime import timezone
import datetime

import pytest
from fixtures.db_fixture import update_db
from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.match_stats import get_match_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_match_stats_view(update_db):
    data = get_match_stats_view(22)
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    team6_id = KHLTeams.objects.get(name='test6').id

    output = {
        'match_info': {
            'arena': 'arena',
            'date': datetime.datetime(2017, 8, 28, 21, 0, tzinfo=timezone.utc),
            'time': datetime.time(15, 0),
            'viewers': 228,
            'season': 21,
            'finished': True,
            'match_stats': [['Team_id', 'Team', 'Sh', 'SoG', 'G', 'FaceOff', 'FaceOff%', 'Hits', 'Blocks', 'Penalty',
                             'TimeA'],
                            [team1_id, 'test1', '66.0', '30.0', '1.0', '26.0', '44.8', '14.0', '14.0', '12.0', '10:37'],
                            [team6_id, 'test6', '44.0', '22.0', '3.0', '32.0', '55.2', '16.0', '22.0', '4.0', '8:41']],
            'season_stats': [
                ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA',
                 'TimeA(A)', 'TimeA%', 'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
                [team1_id, 'test1', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%',
                 '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
                [team6_id, 'test6', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.0', '5.5', '50.00%',
                 '9:39', '9:39', '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']
            ],
        },
        'team1_info': {
            'city': 'city',
            'name': 'test1',
            'image': 'img',
            'id': team1_id,
            'conference': 'conference',
            'division': 'division',
            'arena': 'arena',
            'score': 1,
            'stats': [['Sh', 'SoG', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA', 'Sh(A)', 'SoG(A)', 'G(A)', 'Blocks(A)',
                       'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
                      [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
                      [44, 22, 8, 22, 4, 16, 521, 66, 30, 5, 14, 12, 14, 637],
                      [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
                      [66, 30, 1, 14, 12, 14, 637, 44, 22, 3, 22, 4, 16, 521]],
            'last_matches': '{"19/2017-08-25 21:00:00+00:00": {"date": '
                            '"2017-08-25T21:00:00Z", "time": "15:00:00", '
                            '"id": 19, "team1_name": "test2", '
                            '"team1_score": 8, "team1_image": "img", '
                            '"team1_id": 45, "team2_name": "test1", '
                            '"team2_score": 10, "team2_image": "img", '
                            '"team2_id": 44}, "17/2017-08-23 '
                            '21:00:00+00:00": {"date": '
                            '"2017-08-23T21:00:00Z", "time": "15:00:00", '
                            '"id": 17, "team1_name": "test1", '
                            '"team1_score": 8, "team1_image": "img", '
                            '"team1_id": 44, "team2_name": "test6", '
                            '"team2_score": 5, "team2_image": "img", '
                            '"team2_id": 49}, "15/2017-08-20 '
                            '21:00:00+00:00": {"date": '
                            '"2017-08-20T21:00:00Z", "time": "15:00:00", '
                            '"id": 15, "team1_name": "test1", '
                            '"team1_score": 4, "team1_image": "img", '
                            '"team1_id": 44, "team2_name": "test2", '
                            '"team2_score": 0, "team2_image": "img", '
                            '"team2_id": 45}}',
        },
        'team2_info': {
            'city': 'city',
            'name': 'test6',
            'image': 'img',
            'conference': 'conference',
            'division': 'division',
            'arena': 'arena',
            'score': 3,
            'id': team6_id,
            'stats': [['Sh', 'SoG', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA', 'Sh(A)', 'SoG(A)', 'G(A)', 'Blocks(A)',
                       'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
                      [66, 30, 5, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
                      [66, 30, 5, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
                      [44, 22, 8, 22, 4, 16, 521, 66, 30, 3, 14, 12, 14, 637],
                      [44, 22, 3, 22, 4, 16, 521, 66, 30, 1, 14, 12, 14, 637]],
            'last_matches': '{"20/2017-08-26 21:00:00+00:00": {"date": '
                            '"2017-08-26T21:00:00Z", "time": "15:00:00", '
                            f'"id": 20, "team1_name": "test6", '
                            '"team1_score": 8, "team1_image": "img", '
                            '"team1_id": 49, "team2_name": "test2", '
                            '"team2_score": 3, "team2_image": "img", '
                            '"team2_id": 45}, "18/2017-08-24 '
                            '21:00:00+00:00": {"date": '
                            '"2017-08-24T21:00:00Z", "time": "15:00:00", '
                            '"id": 18, "team1_name": "test2", '
                            '"team1_score": 8, "team1_image": "img", '
                            '"team1_id": 45, "team2_name": "test6", '
                            '"team2_score": 5, "team2_image": "img", '
                            '"team2_id": 49}, "17/2017-08-23 '
                            '21:00:00+00:00": {"date": '
                            '"2017-08-23T21:00:00Z", "time": "15:00:00", '
                            '"id": 17, "team1_name": "test1", '
                            '"team1_score": 8, "team1_image": "img", '
                            '"team1_id": 44, "team2_name": "test6", '
                            '"team2_score": 5, "team2_image": "img", '
                            '"team2_id": 49}}',
        }
    }
    assert data == output

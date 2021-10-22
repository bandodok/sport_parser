from datetime import timezone
import datetime

import pytest
from fixtures.db_fixture import update_db
from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.calendar import get_calendar_view
from sport_parser.khl.view_data.match_stats import get_match_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_calendar_view(update_db):
    out = get_calendar_view(21)
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    team6_id = KHLTeams.objects.get(name='test6').id

    calendar = {'finished_matches': '{"15/2017-08-20 21:00:00+00:00": {"date": '
                                    '"2017-08-20T21:00:00Z", "time": "15:00:00", "id": 15, '
                                    '"team1_name": "test1", "team1_score": 4, "team1_image": '
                                    '"img", "team1_id": 1, "team2_name": "test2", '
                                    '"team2_score": 0, "team2_image": "img", "team2_id": 2}, '
                                    '"17/2017-08-23 21:00:00+00:00": {"date": '
                                    '"2017-08-23T21:00:00Z", "time": "15:00:00", "id": 17, '
                                    '"team1_name": "test1", "team1_score": 8, "team1_image": '
                                    '"img", "team1_id": 1, "team2_name": "test6", '
                                    '"team2_score": 5, "team2_image": "img", "team2_id": 6}, '
                                    '"18/2017-08-24 21:00:00+00:00": {"date": '
                                    '"2017-08-24T21:00:00Z", "time": "15:00:00", "id": 18, '
                                    '"team1_name": "test2", "team1_score": 8, "team1_image": '
                                    '"img", "team1_id": 2, "team2_name": "test6", '
                                    '"team2_score": 5, "team2_image": "img", "team2_id": 6}, '
                                    '"19/2017-08-25 21:00:00+00:00": {"date": '
                                    '"2017-08-25T21:00:00Z", "time": "15:00:00", "id": 19, '
                                    '"team1_name": "test2", "team1_score": 8, "team1_image": '
                                    '"img", "team1_id": 2, "team2_name": "test1", '
                                    '"team2_score": 10, "team2_image": "img", "team2_id": 1}, '
                                    '"20/2017-08-26 21:00:00+00:00": {"date": '
                                    '"2017-08-26T21:00:00Z", "time": "15:00:00", "id": 20, '
                                    '"team1_name": "test6", "team1_score": 8, "team1_image": '
                                    '"img", "team1_id": 6, "team2_name": "test2", '
                                    '"team2_score": 3, "team2_image": "img", "team2_id": 2}, '
                                    '"22/2017-08-28 21:00:00+00:00": {"date": '
                                    '"2017-08-28T21:00:00Z", "time": "15:00:00", "id": 22, '
                                    '"team1_name": "test6", "team1_score": 3, "team1_image": '
                                    '"img", "team1_id": 6, "team2_name": "test1", '
                                    '"team2_score": 1, "team2_image": "img", "team2_id": 1}}',
                'season': 21}
    assert out == calendar

from datetime import datetime, timezone, time

import pytest
from fixtures.db_fixture import update_db
from sport_parser.khl.view_data.match_stats import get_match_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_match_stats_view(update_db):
    data = get_match_stats_view(15)
    output = {
        'match_info': {
            'arena': 'arena',
            'date': datetime(2017, 8, 20, 21, 0, tzinfo=timezone.utc),
            'time': time(15, 0),
            'viewers': 228
        },
        'team1_info': {
            'city': 'city',
            'name': 'test1'
        },
        'team2_info': {
            'city': 'city',
            'name': 'test2'
        }
    }
    assert data == output

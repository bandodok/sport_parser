import pytest
from fixtures.db_fixture import update_db

from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.team_stats import get_team_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_team_stats_view(update_db):
    stats = [
        ['Sh', 'SoG', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA',
         'Sh(A)', 'SoG(A)', 'G(A)', 'Blocks(A)', 'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
        [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
        [44, 22, 8, 22, 4, 16, 521, 66, 30, 5, 14, 12, 14, 637]
    ]
    team1_id = KHLTeams.objects.get(name='test1').id
    out = get_team_stats_view(team1_id)
    assert out == stats

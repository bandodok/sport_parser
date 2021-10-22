import pytest
from fixtures.db_fixture import update_db

from sport_parser.khl.models import KHLTeams
from sport_parser.khl.view_data.season_stats import get_season_stats_view


@pytest.mark.django_db(transaction=True)
def test_get_season_stats_view(update_db):
    team1_id = KHLTeams.objects.get(name='test1').id
    team2_id = KHLTeams.objects.get(name='test2').id
    team6_id = KHLTeams.objects.get(name='test6').id
    stats = [
        ['Team', 'Sh', 'Sh(A)', 'Sh%', 'SoG', 'SoG(A)', 'AQ', 'G', 'G(A)', 'FaceOff%', 'TimeA', 'TimeA(A)', 'TimeA%',
         'DEV%', 'PDO%', 'Hits', 'Blocks', 'Blocks(A)', 'Blocks%', 'Penalty'],
        [team1_id, 'test1', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '6.0', '4.0', '50.00%', '9:39', '9:39',
         '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
        [team2_id, 'test2', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.5', '6.5', '50.00%', '9:39', '9:39',
         '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0'],
        [team6_id, 'test6', '55.0', '55.0', '50.00%', '26.0', '26.0', '47.27%', '5.0', '5.5', '50.00%', '9:39', '9:39',
         '50.00%', '52.73%', '97.27%', '15.0', '18.0', '18.0', '50.00%', '8.0']
    ]
    out = get_season_stats_view(21)
    assert out == stats

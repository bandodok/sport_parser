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
        [team1_id, 'test1', '44.0', '66.0', '40.00%', '22.0', '30.0', '50.00%', '6.0', '2.5', '55.17%', '8:41', '10:37',
         '44.99%', '54.55%', '90.00%', '16.0', '22.0', '14.0', '61.11%', '4.0'],
        [team2_id, 'test2', '66.0', '44.0', '60.00%', '30.0', '22.0', '45.45%', '0.0', '4.0', '44.83%', '10:37', '8:41',
         '55.01%', '50.00%', '105.45%', '14.0', '14.0', '22.0', '38.89%', '12.0'],
        [team6_id, 'test6', '66.0', '44.0', '60.00%', '30.0', '22.0', '45.45%', '5.0', '8.0', '44.83%', '10:37', '8:41',
         '55.01%', '50.00%', '105.45%', '14.0', '14.0', '22.0', '38.89%', '12.0']
    ]
    out = get_season_stats_view(21)
    assert out == stats

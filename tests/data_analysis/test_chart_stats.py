import pytest

from sport_parser.khl.data_analysis.chart_stats import ChartStats
from sport_parser.khl.objects import Team
from sport_parser.khl.config import Config
from fixtures.db_fixture import update_db

from sport_parser.khl.models import KHLTeams


@pytest.mark.django_db(transaction=True)
def test_season_stats_calculate(update_db):
    cs = ChartStats(config=Config)

    team1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    team2_id = KHLTeams.objects.get(name='test2', season_id=21).id
    t1 = Team(team1_id, config=Config)
    t2 = Team(team2_id, config=Config)
    stats_2_teams = cs.calculate([t1, t2])
    assert stats_2_teams == [
        ['test1', 'test1', 'test1', 'test1', 'test1', 'test1', 'test1',
         'test2', 'test2', 'test2', 'test2', 'test2', 'test2', 'test2'],
        [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
        [44, 22, 8, 22, 4, 16, 521, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 1, 14, 12, 14, 637, 66, 30, 3, 14, 12, 14, 637]
    ]

    stats_1_team = cs.calculate(t1)
    assert stats_1_team == [
        ['Sh', 'Sog', 'G', 'Blocks', 'Penalty', 'Hits', 'TimeA', 'Sh(A)',
         'Sog(A)', 'G(A)', 'Blocks(A)', 'Penalty(A)', 'Hits(A)', 'TimeA(A)'],
        [44, 22, 4, 22, 4, 16, 521, 66, 30, 0, 14, 12, 14, 637],
        [44, 22, 8, 22, 4, 16, 521, 66, 30, 5, 14, 12, 14, 637],
        [66, 30, 10, 14, 12, 14, 637, 44, 22, 8, 22, 4, 16, 521],
        [66, 30, 1, 14, 12, 14, 637, 44, 22, 3, 22, 4, 16, 521]
    ]


@pytest.mark.django_db(transaction=True)
def test_get_team_stats_per_day(update_db):
    cs = ChartStats(config=Config)

    team1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    team = Team(team1_id, config=Config)
    stat_list = ['sh', 'sog', 'g', 'time_a']
    stats = cs.get_team_stats_per_day(team, stat_list)
    assert stats == [
        [44, 22, 4, 521],
        [44, 22, 8, 521],
        [66, 30, 10, 637],
        [66, 30, 1, 637]
    ]


@pytest.mark.django_db(transaction=True)
def test_get_opp_stats_per_day(update_db):
    cs = ChartStats(config=Config)

    team1_id = KHLTeams.objects.get(name='test1', season_id=21).id
    team = Team(team1_id, config=Config)
    stat_list = ['sh', 'sog', 'g', 'time_a']
    stats = cs.get_opp_stats_per_day(team, stat_list)
    assert stats == [
        [66, 30, 0, 637],
        [66, 30, 5, 637],
        [44, 22, 8, 521],
        [44, 22, 3, 521]
    ]

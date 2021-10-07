from sport_parser.khl.database_services.db_get import get_team_list, get_team_name, get_team_season_stats


def get_season_stats_view(season):
    """Возвращает список с рассчитанной статистикой команд в виде списков"""
    stats = [[
        'Team',
        'Sh',
        'Sh(A)',
        'Sh%',
        'SoG',
        'SoG(A)',
        'AQ',
        'G',
        'G(A)',
        'FaceOff%',
        'TimeA',
        'TimeA(A)',
        'TimeA%',
        'DEV%',
        'PDO%',
        'Hits',
        'Blocks',
        'Blocks(A)',
        'Blocks%',
        'Penalty',

    ]]
    teams = get_team_list(season)
    for team in teams:
        team_stats = [team, get_team_name(team), ]
        team_stats.extend(get_team_season_stats(team))
        stats.append(team_stats)

    return stats

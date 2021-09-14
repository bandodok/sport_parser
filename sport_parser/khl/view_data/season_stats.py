from sport_parser.khl.database_services.db_get import get_team_list, get_team_name, get_match_list, get_team_stat, \
    get_opponent_stat, sec_to_time, output_format


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
        team_stats = [get_team_name(team), ]
        match_list = get_match_list(team)

        sh = get_team_stat(team, 'sh', match_list, mode='median')
        sog = get_team_stat(team, 'sog', match_list, mode='median')
        g = get_team_stat(team, 'g', match_list, mode='median')
        blocks = get_team_stat(team, 'blocks', match_list, mode='median')
        time_a = get_team_stat(team, 'time_a', match_list, mode='median')
        penalty = get_team_stat(team, 'penalty', match_list, mode='median')
        hits = get_team_stat(team, 'hits', match_list, mode='median')

        sha = get_opponent_stat(team, 'sh', match_list, mode='median')
        soga = get_opponent_stat(team, 'sog', match_list, mode='median')
        ga = get_opponent_stat(team, 'g', match_list, mode='median')
        blocksa = get_opponent_stat(team, 'blocks', match_list, mode='median')
        time_aa = get_opponent_stat(team, 'time_a', match_list, mode='median')

        faceoff = get_team_stat(team, 'faceoff', match_list, mode='sum')
        faceoffa = get_opponent_stat(team, 'faceoff', match_list, mode='sum')

        shp = f'{format(sh / (sh + sha) * 100, ".2f")}%'
        sogp = f'{format(sog / sh * 100, ".2f")}%'
        faceoffp = f'{format(faceoff / (faceoff + faceoffa) * 100, ".2f")}%'
        blocksp = f'{format(blocks / (blocks + blocksa) * 100, ".2f")}%'
        devp = f'{format((1 - (soga / sha)) * 100, ".2f")}%'
        time_ap = f'{format(time_a / (time_a + time_aa) * 100, ".2f")}%'

        pdo = f'{format(((sh / (sh + sha)) + (sog / sh)) * 100, ".2f")}%'

        time_a = sec_to_time(time_a)
        time_aa = sec_to_time(time_aa)

        formated_stats = output_format([
            sh, sha, shp, sog, soga,
            sogp, g, ga, faceoffp,
            time_a, time_aa, time_ap,
            devp, pdo, hits, blocks,
            blocksa, blocksp, penalty
        ])

        team_stats.extend(formated_stats)

        stats.append(team_stats)

    return stats

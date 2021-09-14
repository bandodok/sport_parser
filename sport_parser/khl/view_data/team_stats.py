from sport_parser.khl.database_services.db_get import get_team_list, get_team_name, get_match_list, get_team_stat, \
    get_opponent_stat, sec_to_time, output_format


def get_team_stats_view(team_id):

    match_list = get_match_list(team_id)

    sh = get_team_stat(team_id, 'sh', match_list, mode='list')
    sog = get_team_stat(team_id, 'sog', match_list, mode='list')
    g = get_team_stat(team_id, 'g', match_list, mode='list')
    blocks = get_team_stat(team_id, 'blocks', match_list, mode='list')
 #   time_a = get_team_stat(team_id, 'time_a', match_list, mode='list')
    penalty = get_team_stat(team_id, 'penalty', match_list, mode='list')
    hits = get_team_stat(team_id, 'hits', match_list, mode='list')

    sha = get_opponent_stat(team_id, 'sh', match_list, mode='list')
    soga = get_opponent_stat(team_id, 'sog', match_list, mode='list')
    ga = get_opponent_stat(team_id, 'g', match_list, mode='list')
    blocksa = get_opponent_stat(team_id, 'blocks', match_list, mode='list')
#    time_aa = get_opponent_stat(team_id, 'time_a', match_list, mode='list')

    faceoff = get_team_stat(team_id, 'faceoff', match_list, mode='list')
    faceoffa = get_opponent_stat(team_id, 'faceoff', match_list, mode='list')

    # СДЕЛАТЬ ДЛЯ КАЖДОГО МАТЧА ОТДЕЛЬНО
    shp = []
    for shi, shai in zip(sh, sha):
        shp.append(f'{format(shi / (shi + shai) * 100, ".2f")}%')

    sogp = []
    for sogi, shi in zip(sog, sh):
        sogp.append(f'{format(sogi / shi * 100, ".2f")}%')

    faceoffp = []
    for faceoffi, faceoffai in zip(faceoff, faceoffa):
        faceoffp.append(f'{format(faceoffi / (faceoffi + faceoffai) * 100, ".2f")}%')

    blocksp = []
    for blocksi, blocksai in zip(blocks, blocksa):
        blocksp.append(f'{format(blocksi / (blocksi + blocksai) * 100, ".2f")}%')

    devp = []
    for sogai, shai, in zip(soga, sha):
        devp.append(f'{format((1 - (sogai / shai)) * 100, ".2f")}%')

    time_ap = []
#    for time_ai, time_aai in zip(time_a, time_aa):
#        time_ap.append(f'{format(time_ai / (time_ai + time_aai) * 100, ".2f")}%')

    pdo = []
    for shi, shai, sogi in zip(sh, sha, sog):
        pdo.append(f'{format(((shi / (shi + shai)) + (sogi / shi)) * 100, ".2f")}%')

    output_stats = [[
#       'Team',
        'Sh',
        'Sh(A)',
#        'Sh%',
        'SoG',
        'SoG(A)',
#        'AQ',
        'G',
        'G(A)',
#        'FaceOff%',
#        'TimeA',
#        'TimeA(A)',
#        'TimeA%',
#        'DEV%',
#        'PDO%',
        'Hits',
        'Blocks',
        'Blocks(A)',
#        'Blocks%',
        'Penalty',
    ]]

    for i in range(len(sh)):
        output_stats.append([
        sh[i], sha[i], sog[i], soga[i],
        g[i], ga[i],
        hits[i], blocks[i],
        blocksa[i], penalty[i]
        ])

    for i, row in enumerate(output_stats):
        output_stats[i].insert(0, str(i))

    return output_stats



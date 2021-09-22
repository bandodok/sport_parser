from sport_parser.khl.database_services.db_get import get_team_list, get_team_name, get_match_list, get_team_stat, \
    get_opponent_stat, sec_to_time, output_format, get_team_stats_per_day, get_opp_stats_per_day


def get_team_stats_view(team_id):

    output_stats = [[
        
        'Sh',
        'SoG',
        'G',
        'Blocks',
        'Penalty',
        'Hits',

        'Sh(A)',
        'SoG(A)',
        'G(A)',
        'Blocks(A)',
        'Penalty(A)',
        'Hits(A)',
    ]]

    team_stats = get_team_stats_per_day(team_id, 'sh', 'sog', 'g', 'blocks', 'penalty', 'hits')
    opponent_stats = get_opp_stats_per_day(team_id, 'sh', 'sog', 'g', 'blocks', 'penalty', 'hits')

    for index, value, in enumerate(team_stats):
        value.extend(opponent_stats[index])
        output_stats.append(value)

    return output_stats



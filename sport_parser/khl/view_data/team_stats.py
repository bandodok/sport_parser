from sport_parser.khl.database_services.db_get import get_team_stats_per_day, get_opp_stats_per_day, time_to_sec


def get_team_stats_view(team_id):

    output_stats = [[
        
        'Sh',
        'SoG',
        'G',
        'Blocks',
        'Penalty',
        'Hits',
        'TimeA',

        'Sh(A)',
        'SoG(A)',
        'G(A)',
        'Blocks(A)',
        'Penalty(A)',
        'Hits(A)',
        'TimeA(A)'
    ]]

    team_stats = get_team_stats_per_day(team_id, 'sh', 'sog', 'g', 'blocks', 'penalty', 'hits', 'time_a')
    opponent_stats = get_opp_stats_per_day(team_id, 'sh', 'sog', 'g', 'blocks', 'penalty', 'hits', 'time_a')

    for index, value, in enumerate(team_stats):
        value.extend(opponent_stats[index])
        value[6] = time_to_sec(value[6])
        value[13] = time_to_sec(value[13])
        output_stats.append(value)

    return output_stats



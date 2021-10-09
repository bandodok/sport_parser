from sport_parser.khl.database_services.db_get import get_match_by_id, get_team_season_stats
from sport_parser.khl.view_data.team_stats import get_team_stats_view


def get_match_stats_view(match_id):
    match = get_match_by_id(match_id)
    team1, team2 = match.teams.all()

    team1_season_stats = [team1.name, team1.id]
    team2_season_stats = [team2.name, team2.id]

    team1_season_stats.extend(get_team_season_stats(team1.id))
    team2_season_stats.extend(get_team_season_stats(team2.id))

    season_stats = [[
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
    ],
        team1_season_stats,
        team2_season_stats
    ]

    match_info = {
        'date': match.date,
        'time': match.time,
        'arena': match.arena,
        'viewers': match.viewers,
        'season_stats': season_stats,
        'finished': match.finished
    }

    exclude = 0
    if match_info['finished']:
        exclude = match.match_id

    team1_last_matches_query = team1.last_matches(5, exclude=exclude)
    team2_last_matches_query = team2.last_matches(5, exclude=exclude)

    team1_last_matches = _last_matches_info(team1_last_matches_query)
    team2_last_matches = _last_matches_info(team2_last_matches_query)

    team1_info = {
        'name': team1.name,
        'city': team1.city,
        'stats': get_team_stats_view(team1.id),
        'last_matches': team1_last_matches
    }
    team2_info = {
        'name': team2.name,
        'city': team2.city,
        'stats': get_team_stats_view(team2.id),
        'last_matches': team2_last_matches
    }

    return {
        'match_info': match_info,
        'team1_info': team1_info,
        'team2_info': team2_info
    }


def _last_matches_info(matches):
    last_matches = {}
    for match in matches:
        last_matches[match.match_id] = {
            'date': match.date,
            'time': match.time,
            'team1_name': match.khlprotocol_set.all()[0].team_id.name,
            'team1_score': match.khlprotocol_set.all()[0].g,
            'team2_name': match.khlprotocol_set.all()[1].team_id.name,
            'team2_score': match.khlprotocol_set.all()[1].g,
        }
    return last_matches

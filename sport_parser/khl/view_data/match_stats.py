from sport_parser.khl.database_services.db_get import get_match_by_id


def get_match_stats_view(match_id):
    match = get_match_by_id(match_id)
    team1, team2 = match.teams.all()

    match_info = {
        'date': match.date,
        'time': match.time,
        'arena': match.arena,
        'viewers': match.viewers
    }

    team1_info = {
        'name': team1.name,
        'city': team1.city,
    }
    team2_info = {
        'name': team2.name,
        'city': team2.city,
    }

    return {
        'match_info': match_info,
        'team1_info': team1_info,
        'team2_info': team2_info
    }

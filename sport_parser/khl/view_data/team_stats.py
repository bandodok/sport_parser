from sport_parser.khl.database_services.db_get import get_team_by_id, get_team_id_by_season, get_team_chart_stats


def get_team_stats_view(team_id):

    output_stats = get_team_chart_stats(team_id)

    team = get_team_by_id(team_id)
    name = team.name
    arena = team.arena
    city = team.city
    division = team.division
    conference = team.conference
    logo = team.img
    season = team.season
    season_dict = get_team_id_by_season(team_id)
    last_matches = last_matches_info(team.last_matches(5))
    future_matches = future_matches_info(team.future_matches(5))

    return {
        'stats': output_stats,
        'team': name,
        'arena': arena,
        'city': city,
        'division': division,
        'conference': conference,
        'logo': logo,
        'season': season,
        'seasons': season_dict,
        'last_matches': last_matches,
        'future_matches': future_matches
    }


def last_matches_info(matches):
    last_matches = {}
    for match in matches:
        last_matches[match.match_id] = {
            'date': match.date,
            'time': match.time,
            'team1_name': match.khlprotocol_set.all()[0].team_id.name,
            'team1_score': match.khlprotocol_set.all()[0].g,
            'team1_image': match.khlprotocol_set.all()[0].team_id.img,
            'team1_id': match.khlprotocol_set.all()[0].team_id.id,
            'team2_name': match.khlprotocol_set.all()[1].team_id.name,
            'team2_score': match.khlprotocol_set.all()[1].g,
            'team2_image': match.khlprotocol_set.all()[1].team_id.img,
            'team2_id': match.khlprotocol_set.all()[1].team_id.id,
        }
    return last_matches


def future_matches_info(matches):
    future_matches = {}
    for match in matches:
        future_matches[match.match_id] = {
            'date': match.date,
            'time': match.time,
            'team1_name': match.teams.all()[0].name,
            'team1_image': match.teams.all()[0].img,
            'team1_id': match.teams.all()[0].id,
            'team2_name': match.teams.all()[1].name,
            'team2_image': match.teams.all()[1].img,
            'team2_id': match.teams.all()[1].id,
        }
    return future_matches

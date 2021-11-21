import json
from django.core.serializers.json import DjangoJSONEncoder

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
        'season': season.id,
        'seasons': season_dict,
        'last_matches': last_matches,
        'future_matches': future_matches
    }


def last_matches_info(matches):
    last_matches = {}
    for match in matches:
        protocol1, protocol2 = match.protocols.all()
        last_matches[f'{match.id}/{match.date}'] = {
            'date': match.date,
            'time': match.time,
            'id': match.id,
            'team1_name': protocol1.team.name,
            'team1_score': protocol1.g,
            'team1_image': protocol1.team.img,
            'team1_id': protocol1.team.id,
            'team2_name': protocol2.team.name,
            'team2_score': protocol2.g,
            'team2_image': protocol2.team.img,
            'team2_id': protocol2.team.id,
        }
    return json.dumps(last_matches, cls=DjangoJSONEncoder)


def future_matches_info(matches):
    future_matches = {}
    for match in matches:
        team1, team2 = match.teams.all()
        future_matches[f'{match.id}/{match.date}'] = {
            'date': match.date,
            'time': match.time,
            'id': match.id,
            'team1_name': team1.name,
            'team1_image': team1.img,
            'team1_id': team1.id,
            'team2_name': team2.name,
            'team2_image': team2.img,
            'team2_id': team2.id,
        }
    return json.dumps(future_matches, cls=DjangoJSONEncoder)

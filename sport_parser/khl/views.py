from sport_parser.khl.database_services.db_add import last_updated
from sport_parser.khl.database_services.db_get import get_team_attr, get_team_id_by_season
from sport_parser.khl.parsers.season import parse_season, update_protocols, parse_season_matches
from sport_parser.khl.parsers.team_info import parse_teams
from sport_parser.khl.parsers.score_table import get_score_table
from sport_parser.khl.view_data.match_stats import get_match_stats_view
from sport_parser.khl.view_data.season_stats import get_season_stats_view
from sport_parser.khl.view_data.team_stats import get_team_stats_view
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect


def index(request):
    data = get_score_table()
    return HttpResponse(data.to_html())
   # return render(request, 'khl_index.html', context={'data': data.to_html()})


def update(request, match_id):
    parse_season(match_id)
    return HttpResponse('Complete!')


def update_teams(request):
    parse_teams()
    return HttpResponse('Complete!')


def stats(request, season):
    update_date = last_updated()
    stats = get_season_stats_view(season)
    if len(stats) == 1:
        raise Http404("Season does not exist")
    return render(request, 'khl_stats.html', context={'stats': stats, 'update': update_date, 'season': season})


def team(request, team_id):
    team_stats = get_team_stats_view(team_id)
    team = get_team_attr(team_id, 'name')
    arena = get_team_attr(team_id, 'arena')
    city = get_team_attr(team_id, 'city')
    division = get_team_attr(team_id, 'division')
    conference = get_team_attr(team_id, 'conference')
    logo = get_team_attr(team_id, 'img')
    season = get_team_attr(team_id, 'season')
    season_dict = get_team_id_by_season(team_id)
    return render(request, 'khl_team.html', context={
        'stats': team_stats,
        'team': team,
        'arena': arena,
        'city': city,
        'division': division,
        'conference': conference,
        'logo': logo,
        'season': season,
        'seasons': season_dict
    })


def match(request, match_id):
    context = get_match_stats_view(match_id)
    return render(request, 'khl_match.html', context=context)


def update_protocol(request):
    update_protocols()
    return redirect('/khl/stats/21')


def update_season_matches(request, season):
    parse_season_matches(season)
    return redirect('/khl/stats/21')

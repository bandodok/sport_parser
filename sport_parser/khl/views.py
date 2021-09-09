from sport_parser.khl.database_services.db_add import last_updated
from sport_parser.khl.parsers.match_protocol import parse_season, update_protocols
from sport_parser.khl.parsers.team_info import parse_teams
from sport_parser.khl.parsers.score_table import get_score_table
from sport_parser.khl.view_data.season_stats import get_team_stats_view
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
    stats = get_team_stats_view(season)
    if len(stats) == 1:
        raise Http404("Season does not exist")
    return render(request, 'khl_stats.html', context={'stats': stats, 'update': update_date, 'season': season})


def update_protocol(request):
    update_protocols()
    return redirect('/khl/stats/21')

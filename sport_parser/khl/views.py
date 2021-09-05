from sport_parser.parsers.parser import get_score_table, parse_season, parse_teams, update_protocols, last_updated
from sport_parser.database_services.database import get_team_stats_view
from django.http import HttpResponse
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
    return render(request, 'khl_stats.html', context={'stats': stats, 'update': update_date})


def update_protocol(request):
    update_protocols()
    return redirect('/khl/stats/21')


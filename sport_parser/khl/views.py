from sport_parser.parsers.parser import get_teams, parse_season
from sport_parser.database_services.database import get_team_stats_view
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    data = get_teams()
    return HttpResponse(data.to_html())
   # return render(request, 'khl_index.html', context={'data': data.to_html()})


def update(request, match_id):
    parse_season(match_id)
    return HttpResponse('Complete!')


def stats(request):
    stats = get_team_stats_view()
    return render(request, 'khl_stats.html', context={'stats': stats})

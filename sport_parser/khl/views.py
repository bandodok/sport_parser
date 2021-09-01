from sport_parser.parsers.parser import get_teams, parse_season
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    data = get_teams()
    return HttpResponse(data.to_html())
   # return render(request, 'khl_index.html', context={'data': data.to_html()})


def update(request, match_id):
    parse_season(match_id)
    return HttpResponse('Complete!')

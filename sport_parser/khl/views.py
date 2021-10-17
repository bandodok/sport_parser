from sport_parser.khl.database_services.db_add import last_updated
from sport_parser.khl.parsers.season import update_protocols, parse_season_matches
from sport_parser.khl.parsers.team_info import parse_teams
from sport_parser.khl.parsers.score_table import get_score_table
from sport_parser.khl.view_data.calendar import get_calendar_view, get_calendar_finished, get_calendar_unfinished
from sport_parser.khl.view_data.match_stats import get_match_stats_view
from sport_parser.khl.view_data.season_stats import get_season_stats_view
from sport_parser.khl.view_data.team_stats import get_team_stats_view
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect


def index(request):
    data = get_score_table()
    return HttpResponse(data.to_html())
   # return render(request, 'khl_index.html', context={'data': data.to_html()})


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
    return render(request, 'khl_team.html', context=get_team_stats_view(team_id))


def match(request, match_id):
    context = get_match_stats_view(match_id)
    return render(request, 'khl_match.html', context=context)


def calendar(request, season):
    return render(request, 'khl_calendar.html', context=get_calendar_view(season))


def calendar_f(request, season):
    return JsonResponse(get_calendar_finished(season))


def calendar_u(request, season):
    return JsonResponse(get_calendar_unfinished(season))


def update_protocol(request):
    update_protocols()
    return redirect('/khl/stats/21')


def update_finished(request, season):
    update_protocols(season, finished=True)
    return HttpResponse('Complete!')


def update_season_matches(request, season):
    parse_season_matches(season)
    return redirect('/khl/stats/21')

from sport_parser.khl.objects import Season, Team, Match
from sport_parser.khl.parsers.season import update_protocols, parse_season_matches
from sport_parser.khl.parsers.team_info import parse_teams
from sport_parser.khl.parsers.score_table import get_score_table
from sport_parser.khl.view_data.calendar import get_calendar_view, get_calendar_finished, get_calendar_unfinished
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect


def index(request):
    data = get_score_table()
    return HttpResponse(data.to_html())
   # return render(request, 'khl_index.html', context={'data': data.to_html()})


def update_teams(request):
    parse_teams()
    return HttpResponse('Complete!')


def stats(request, season):
    s = Season(season)
    if s.season_does_not_exist:
        raise Http404("Season does not exist")
    context = {
        'update': s.last_updated(),
        'stats': s.get_table_stats(),
        'season': season
    }
    return render(request, 'khl_stats.html', context=context)


def team(request, team_id):
    t = Team(team_id)
    context = {
        'stats': t.get_chart_stats(),
        'team': t.data,
        'seasons': t.get_another_season_team_ids(),
        'last_matches': t.get_json_last_matches(5),
        'future_matches': t.get_json_future_matches(5)
    }
    return render(request, 'khl_team.html', context=context)


def match(request, match_id):
    m = Match(match_id)
    context = {
        'match': m.data,
        'match_stats': m.get_match_stats(),
        'season_stats': m.get_table_stats(),
        'chart_stats': m.get_chart_stats(),
        'team1': {
            'data': m.team1.data,
            'score': m.get_team1_score(),
            'last_matches': m.get_team1_last_matches(5)
        },
        'team2': {
            'data': m.team2.data,
            'score': m.get_team2_score(),
            'last_matches': m.get_team2_last_matches(5)
        },
    }
    return render(request, 'khl_match.html', context=context)


def calendar(request, season):
    return render(request, 'khl_calendar.html', context=get_calendar_view(season))


def calendar_f(request, season):
    return HttpResponse(get_calendar_finished(season), content_type='application/json')


def calendar_u(request, season):
    return HttpResponse(get_calendar_unfinished(season), content_type='application/json')


def update_protocol(request):
    update_protocols()
    return redirect('/khl/stats/21')


def update_finished(request, season):
    update_protocols(season, finished=True)
    return HttpResponse('Complete!')


def update_season_matches(request, season):
    parse_season_matches(season)
    return redirect('/khl/stats/21')

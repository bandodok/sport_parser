from sport_parser.parsers.parser import get_score_table, parse_season, parse_teams
from sport_parser.database_services.database import get_team_stats_view
from django.http import HttpResponse
from django.shortcuts import redirect


def index(request):
    return redirect('/khl/stats/21')


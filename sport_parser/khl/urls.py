from django.urls import path
from sport_parser.khl.views import index, update_finished, stats, team, match, update_teams, update_protocol,\
    update_season_matches, calendar
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', index),

    path('stats/<int:season>', stats, name='stats'),
    path('team/<int:team_id>', team, name='team'),
    path('match/<int:match_id>/', match, name='match'),
    path('calendar/<int:season>/', calendar, name='calendar'),

    path('update/teams/', update_teams),
    path('update/season_matches/<int:season>', update_season_matches),
    path('update/finished_protocol/<int:season>/', update_finished),
    path('update/protocol/', update_protocol),
]

urlpatterns += staticfiles_urlpatterns()

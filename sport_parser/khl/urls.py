from django.urls import path
from sport_parser.khl.views import index, update, stats, team, match, update_teams, update_protocol,\
    update_season_matches, calendar
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', index),

    path('stats/<int:season>', stats, name='stats'),
    path('team/<int:team_id>', team, name='team'),
    path('match/<int:match_id>/', match, name='match'),
    path('calendar/<int:season>/', calendar, name='calendar'),

    path('update/teams/', update_teams),
    path('update/protocol/', update_protocol),
    path('update/<int:match_id>/', update),
    path('update/season_matches/<int:season>', update_season_matches),
]

urlpatterns += staticfiles_urlpatterns()

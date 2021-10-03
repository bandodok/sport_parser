from django.urls import path
from sport_parser.khl.views import index, update, stats, update_teams, update_protocol, team, update_season_matches
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', index),

    path('update/<int:match_id>/', update),
    path('stats/<int:season>', stats, name='stats'),
    path('team/<int:team_id>', team, name='team'),

    path('update/teams/', update_teams),
    path('update/protocol/', update_protocol),
    path('update/season_matches/<int:season>', update_season_matches),
]

urlpatterns += staticfiles_urlpatterns()

from django.urls import path
from sport_parser.khl.views import index, update, stats, update_teams, update_protocol, team
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', index),
    path('update/<int:match_id>/', update),
    path('update/teams/', update_teams),
    path('stats/<int:season>', stats, name='stats'),
    path('update/protocol/', update_protocol),
    path('team/<int:team_id>', team, name='team')
]

urlpatterns += staticfiles_urlpatterns()

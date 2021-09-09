from django.urls import path
from sport_parser.khl.views import index, update, stats, update_teams, update_protocol


urlpatterns = [
    path('', index),
    path('update/<int:match_id>/', update),
    path('update/teams/', update_teams),
    path('stats/<int:season>', stats),
    path('update/protocol/', update_protocol)
]

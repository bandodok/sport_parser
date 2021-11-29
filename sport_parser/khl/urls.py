from django.urls import path
from sport_parser.khl.views import stats, team, match, update_protocol, update_season_matches, calendar
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('stats/<int:season>', stats, name='stats'),
    path('team/<int:team_id>', team, name='team'),
    path('match/<int:match_id>/', match, name='match'),
    path('calendar/<int:season>/', calendar, name='calendar'),

    path('update/season_matches/<int:season>', update_season_matches),
    path('update/protocol/', update_protocol),
]

urlpatterns += staticfiles_urlpatterns()

from django.urls import path
from sport_parser.khl.views import UpdateView, UpdateSeasonView, CalendarView, StatsView, TeamView, MatchView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('stats/<int:season_id>', StatsView.as_view(), name='stats'),
    path('team/<int:team_id>', TeamView.as_view(), name='team'),
    path('match/<int:match_id>/', MatchView.as_view(), name='match'),
    path('calendar/<int:season_id>/', CalendarView.as_view(), name='calendar'),

    path('update/season/<int:season>', UpdateSeasonView.as_view()),
    path('update/protocol/', UpdateView.as_view()),
]

urlpatterns += staticfiles_urlpatterns()

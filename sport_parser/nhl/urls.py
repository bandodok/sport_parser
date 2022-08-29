from django.urls import path
from sport_parser.nhl.views import NHLUpdateView, NHLUpdateSeasonView, NHLCalendarView, NHLStatsView, NHLTeamView, NHLMatchView, NHLCalendarApi
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


app_name = 'nhl'
urlpatterns = [
    path('stats/', NHLStatsView.as_view(), name='last_stats'),
    path('stats/<int:season_id>', NHLStatsView.as_view(), name='stats'),
    path('team/<int:team_id>', NHLTeamView.as_view(), name='team'),
    path('match/<int:match_id>/', NHLMatchView.as_view(), name='match'),
    path('calendar/<int:season_id>/', NHLCalendarView.as_view(), name='calendar'),

    path('update/season/<int:season>', NHLUpdateSeasonView.as_view()),
    path('update/protocol/', NHLUpdateView.as_view()),

    path('stats/', NHLStatsView.as_view(), name='index_stats'),
    path('team/', NHLTeamView.as_view(), name='index_team'),
    path('match/', NHLMatchView.as_view(), name='index_match'),
    path('calendar/', NHLCalendarView.as_view(), name='index_calendar'),
]

urlpatterns += staticfiles_urlpatterns()
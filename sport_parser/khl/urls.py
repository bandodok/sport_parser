from django.urls import path
from sport_parser.khl.views import KHLStatsView, KHLTeamView, KHLMatchView, KHLCalendarView, KHLUpdateSeasonView, \
    KHLUpdateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


app_name = 'khl'
urlpatterns = [
    path('stats/<int:season_id>', KHLStatsView.as_view(), name='stats'),
    path('team/<int:team_id>', KHLTeamView.as_view(), name='team'),
    path('match/<int:match_id>/', KHLMatchView.as_view(), name='match'),
    path('calendar/<int:season_id>/', KHLCalendarView.as_view(), name='calendar'),

    path('update/season/<int:season>', KHLUpdateSeasonView.as_view()),
    path('update/protocol/', KHLUpdateView.as_view()),

    path('stats/', KHLStatsView.as_view(), name='index_stats'),
    path('team/', KHLTeamView.as_view(), name='index_team'),
    path('match/', KHLMatchView.as_view(), name='index_match'),
    path('calendar/', KHLCalendarView.as_view(), name='index_calendar'),
]

urlpatterns += staticfiles_urlpatterns()

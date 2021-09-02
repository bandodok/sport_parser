from django.urls import path
from sport_parser.khl.views import index, update, stats


urlpatterns = [
    path('', index),
    path('update/<int:match_id>', update),
    path('stats/', stats)
]
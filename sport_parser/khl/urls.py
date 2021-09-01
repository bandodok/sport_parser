from django.urls import path
from sport_parser.khl.views import index, update


urlpatterns = [
    path('', index),
    path('update/<int:match_id>', update),
]
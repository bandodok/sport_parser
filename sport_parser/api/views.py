from rest_framework import generics

from .serializers import CalendarSerializer, LiveMatchSerializer
from sport_parser.core.creator import Creator
from django.db.models import Q


class Calendar(generics.ListAPIView):
    serializer_class = CalendarSerializer
    ordering_fields = ['date']
    filterset_fields = ['teams', 'status', 'season']

    def get_queryset(self):
        config = self.request.query_params['config']
        self.request.app_name = config
        creator = Creator(self.request)
        season = creator.get_season_class(self.request.query_params['season'])
        return season.models.match_model.objects.all().order_by('date')


class LiveMatch(generics.ListAPIView):
    serializer_class = LiveMatchSerializer
    ordering_fields = ['id']

    def get_queryset(self):
        config = self.request.query_params['league']
        creator = Creator(config)
        match = creator.get_match_class(self.request.query_params['match_id'])
        return match.models.match_model.objects\
            .filter(id=self.request.query_params['match_id'])\
            .filter(Q(status='live') | Q(status='game over'))

from rest_framework import generics
from sport_parser.core.models import LiveMatches

from .serializers import CalendarSerializer, LiveMatchSerializer
from sport_parser.core.creator import Creator


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
    ordering_fields = ['match_id']
    filterset_fields = ['league', 'match_id']

    def get_queryset(self):
        return LiveMatches.objects.all()

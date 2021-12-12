from rest_framework import generics

from .filters import CalendarFilter
from .serializers import CalendarSerializer
from sport_parser.khl.config import Creator


class Calendar(generics.ListAPIView):
    serializer_class = CalendarSerializer
    filterset_class = CalendarFilter
    ordering_fields = ['date']
    filterset_fields = ['teams', 'finished', 'season']

    def get_queryset(self):
        config = 'khl'
        self.request.app_name = config
        creator = Creator(self.request)
        season = creator.get_season_class(self.request.query_params['season'])
        return season.models.match_model.objects.all().order_by('date', 'time')

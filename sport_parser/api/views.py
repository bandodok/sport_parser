from rest_framework import generics

from .serializers import CalendarSerializer
from ..khl.creator import Creator


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

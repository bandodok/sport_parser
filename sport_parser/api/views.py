from rest_framework import generics

from .filters import CalendarFilter
from .serializers import CalendarSerializer
from sport_parser.khl.objects import Season


class Calendar(generics.ListAPIView):
    serializer_class = CalendarSerializer
    filterset_class = CalendarFilter
    queryset = Season.models.match_model.objects.all().order_by('date', 'time')

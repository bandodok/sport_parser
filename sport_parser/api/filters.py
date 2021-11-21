from django_filters import rest_framework as filters
from sport_parser.khl.objects import Season


def teams_field(request):
    if request is None:
        return Season.models.team_model.objects.all().order_by('name')

    season = request.query_params.get('season')
    return Season.models.team_model.objects.filter(season=season).order_by('name')


class CalendarFilter(filters.FilterSet):
    teams = filters.ModelChoiceFilter(
        queryset=teams_field,
    )

    class Meta:
        model = Season.models.match_model
        fields = ['teams', 'finished', 'season']

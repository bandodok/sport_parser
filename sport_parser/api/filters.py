from django_filters import rest_framework as filters
from sport_parser.khl.config import Config
from sport_parser.khl.creator import Creator


def teams_field(request):
    if request is None:
        return
    creator = Creator(request)
    season = request.query_params.get('season')
    team_model = creator.get_season_class(season).models.team_model
    return team_model.objects.filter(season=season).order_by('name')


def get_model(request):
    if request is None:
        return
    creator = Creator(request.app_name)
    season = request.query_params.get('season')
    team_model = creator.get_season_class(season).models.team_model
    return team_model.objects.filter(season=season).order_by('name')


class CalendarFilter(filters.FilterSet):
    teams = filters.ModelChoiceFilter(
        queryset=teams_field,
    )

    class Meta:
        model = Config.models.match_model
        fields = ['teams', 'finished', 'season']

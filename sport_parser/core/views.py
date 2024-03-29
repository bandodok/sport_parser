from abc import abstractmethod

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from sport_parser.core.configs import ConfigType
from sport_parser.core.creator import Creator
from sport_parser.core.exceptions import SeasonDoesNotExist, TeamDoesNotExist, MatchDoesNotExist
from sport_parser.core.objects import Season, Team, Match
from sport_parser.core.tasks import update, parse_season


class HockeyView(View):
    config: ConfigType = ConfigType.khl
    template: str = ''
    creator: Creator = None

    def get(self, request, **kwargs):
        self.creator = Creator(self.config)
        object1 = self.get_object(*kwargs.values())
        context = self.get_context(object1)
        context.update(self.get_meta_context())
        return render(request, self.template, context=context)

    @abstractmethod
    def get_context(self, s):
        pass

    @abstractmethod
    def get_object(self, *args):
        pass

    def get_meta_context(self):
        return {
            'theme': self.get_theme(),
            'background_image': self.get_background_image(),
            'title': self.get_title(),
            'league_title': self.get_league_title(),
            'league_logo': self.get_league_logo(),
            'config': self.config.name,
            'glossary': self.get_glossary(),
            'league': self.config.name,
            'season_list': self.creator.get_season_list(),

            'url_stats': reverse_lazy(f'{self.config.name}:index_stats'),
            'url_team': reverse_lazy(f'{self.config.name}:index_team'),
            'url_match': reverse_lazy(f'{self.config.name}:index_match'),
            'url_calendar': reverse_lazy(f'{self.config.name}:index_calendar'),
            'url_calendar_api': reverse_lazy(f'{self.config.name}_calendar_api'),
        }

    def get_theme(self):
        return f'css/themes/{self.creator.get_theme()}'

    def get_background_image(self):
        return f'/static/img/{self.creator.get_background_image()}'

    def get_title(self):
        return self.creator.get_title()

    def get_league_title(self):
        return self.creator.get_league_title()

    def get_league_logo(self):
        return f'/static/img/{self.creator.get_league_logo()}'

    def get_glossary(self):
        return self.creator.get_glossary()


class StatsView(HockeyView):
    config: ConfigType = ConfigType.khl
    template: str = 'khl_stats.html'

    def get_object(self, season_id=0) -> Season:
        try:
            s = self.creator.get_season_class(season_id)
        except SeasonDoesNotExist:
            raise Http404("Season does not exist")
        return s

    def get_context(self, s: Season):
        return {
            'update': s.last_updated(),
            'stats': s.get_table_stats(),
            'season': s.data.id,
            'last_matches': s.get_json_last_matches(6),
            'future_matches': s.get_json_future_matches(6),
            'live_matches': s.get_json_live_matches()
        }


class TeamView(HockeyView):
    config: ConfigType = ConfigType.khl
    template: str = 'khl_team.html'

    def get_object(self, team_id=0) -> Team:
        try:
            team = self.creator.get_team_class(team_id)
        except TeamDoesNotExist:
            raise Http404("Team does not exist")
        return team

    def get_context(self, t: Team):
        return {
            'stats': t.get_chart_stats(),
            'team': t.data,
            'seasons': t.get_another_season_team_ids(),
            'last_matches': t.get_json_last_matches(6),
            'future_matches': t.get_json_future_matches(6)
        }


class MatchView(HockeyView):
    config: ConfigType = ConfigType.khl
    template: str = 'khl_match.html'

    def get_object(self, match_id=0) -> Match:
        try:
            match = self.creator.get_match_class(match_id)
        except MatchDoesNotExist:
            raise Http404("Match does not exist")
        return match

    def get_context(self, m: Match):
        return {
            'match': m.data,
            'match_stats': m.get_bar_stats(),
            'season_stats': m.get_table_stats(),
            'chart_stats': m.get_chart_stats(),
            'overtime': m.data.overtime,
            'penalties': m.data.penalties,
            'team1': {
                'data': m.team1.data,
                'score': m.get_team1_score_by_period(),
                'last_matches': m.get_team1_last_matches(6)
            },
            'team2': {
                'data': m.team2.data,
                'score': m.get_team2_score_by_period(),
                'last_matches': m.get_team2_last_matches(6)
            },
        }


class CalendarView(HockeyView):
    config: ConfigType = ConfigType.khl
    template: str = 'khl_calendar.html'

    def get_object(self, season_id=0) -> Season:
        return self.creator.get_season_class(season_id)

    def get_context(self, s: Season):
        return {
            'season': s.data.id,
            'teams': s.get_team_list()
        }


class UpdateView(View):
    config: ConfigType = ConfigType.khl

    def get(self, request):
        update.delay(self.config.name)
        return render(request, 'ws_update.html', {})


class UpdateSeasonView(View):
    config: ConfigType = ConfigType.khl

    def get(self, request, season: int):
        parse_season.delay(self.config.name, season)
        return render(request, 'ws_update.html', {})

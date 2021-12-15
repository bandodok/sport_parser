from abc import abstractmethod

from django.http import Http404
from django.shortcuts import render
from django.views import View

from sport_parser.khl.creator import Creator
from sport_parser.khl.tasks import update, parse_season


class HockeyView(View):
    config = 'khl'
    template = ''

    def get(self, request, **kwargs):
        request.app_name = self.config
        self.creator = Creator(request)
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


class StatsView(HockeyView):
    config = 'khl'
    template = 'khl_stats.html'

    def get_object(self, season_id):
        s = self.creator.get_season_class(season_id)
        if s.season_does_not_exist:
            raise Http404("Season does not exist")
        return s

    def get_context(self, s):
        return {
            'update': s.last_updated(),
            'stats': s.get_table_stats(),
            'season': s.data.id,
            'last_matches': s.get_json_last_matches(5),
            'future_matches': s.get_json_future_matches(5)
        }


class TeamView(HockeyView):
    config = 'khl'
    template = 'khl_team.html'

    def get_object(self, team_id):
        return self.creator.get_team_class(team_id)

    def get_context(self, t):
        return {
            'stats': t.get_chart_stats(),
            'team': t.data,
            'seasons': t.get_another_season_team_ids(),
            'last_matches': t.get_json_last_matches(5),
            'future_matches': t.get_json_future_matches(5)
        }


class MatchView(HockeyView):
    config = 'khl'
    template = 'khl_match.html'

    def get_object(self, match_id):
        return self.creator.get_match_class(match_id)

    def get_context(self, m):
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
                'last_matches': m.get_team1_last_matches(5)
            },
            'team2': {
                'data': m.team2.data,
                'score': m.get_team2_score_by_period(),
                'last_matches': m.get_team2_last_matches(5)
            },
        }


class CalendarView(HockeyView):
    config = 'khl'
    template = 'khl_calendar.html'

    def get_object(self, season_id):
        return self.creator.get_season_class(season_id)

    def get_context(self, s):
        return {
            'season': s.data.id,
            'teams': s.get_team_list()
        }


class UpdateView(View):
    config = 'khl'

    def get(self, request):
        update.delay(self.config)
        return render(request, 'ws_update.html', {})


class UpdateSeasonView(View):
    config = 'khl'

    def get(self, request, season):
        parse_season.delay(self.config, season)
        return render(request, 'ws_update.html', {})

from abc import abstractmethod

from django.http import Http404
from django.shortcuts import render, redirect
from sport_parser.khl.config import Creator

from django.views import View


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


class StatsView(View):
    config = 'khl'

    def get(self, request, season_id):
        request.app_name = self.config
        creator = Creator(request)
        s = creator.get_season_class(season_id)
        if s.season_does_not_exist:
            raise Http404("Season does not exist")
        context = {
            'update': s.last_updated(),
            'stats': s.get_table_stats(),
            'season': season_id
        }
        return render(request, 'khl_stats.html', context=context)


class TeamView(View):
    config = 'khl'

    def get(self, request, team_id):
        request.app_name = self.config
        creator = Creator(request)
        t = creator.get_team_class(team_id)

        context = {
            'stats': t.get_chart_stats(),
            'team': t.data,
            'seasons': t.get_another_season_team_ids(),
            'last_matches': t.get_json_last_matches(5),
            'future_matches': t.get_json_future_matches(5)
        }
        return render(request, 'khl_team.html', context=context)


class MatchView(View):
    config = 'khl'

    def get(self, request, match_id):
        request.app_name = self.config
        creator = Creator(request)
        m = creator.get_match_class(match_id)

        context = {
            'match': m.data,
            'match_stats': m.get_match_stats(),
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
        return render(request, 'khl_match.html', context=context)


class CalendarView(View):
    config = 'khl'

    def get(self, request, season_id):
        request.app_name = self.config
        creator = Creator(request)
        s = creator.get_season_class(season_id)

        context = {
            'season': season_id,
            'teams': s.get_team_list()
        }
        return render(request, 'khl_calendar.html', context=context)


class UpdateView(View):
    config = 'khl'

    def get(self, request):
        request.app_name = self.config
        creator = Creator(request)
        u = creator.get_updater()

        u.update()
        return redirect('/khl/stats/21')


class UpdateSeasonView(View):
    config = 'khl'

    def get(self, request, season):

        request.app_name = self.config
        creator = Creator(request)
        u = creator.get_updater()

        u.parse_season(season)
        return redirect('/khl/stats/21')

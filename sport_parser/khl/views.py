from django.http import Http404
from django.shortcuts import render, redirect
from sport_parser.khl.config import Creator

from django.views import View


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

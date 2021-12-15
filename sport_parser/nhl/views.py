from sport_parser.khl.views import StatsView, TeamView, MatchView, CalendarView, UpdateView, UpdateSeasonView
from sport_parser.api.views import Calendar


class NHLStatsView(StatsView):
    config = 'nhl'


class NHLMatchView(MatchView):
    config = 'nhl'


class NHLTeamView(TeamView):
    config = 'nhl'


class NHLCalendarView(CalendarView):
    config = 'nhl'


class NHLCalendarApi(Calendar):
    config = 'nhl'


class NHLUpdateView(UpdateView):
    config = 'nhl'


class NHLUpdateSeasonView(UpdateSeasonView):
    config = 'nhl'

from sport_parser.core.configs import ConfigType
from sport_parser.core.views import StatsView, TeamView, MatchView, CalendarView, UpdateView, UpdateSeasonView
from sport_parser.api.views import Calendar


class NHLStatsView(StatsView):
    config = ConfigType.nhl


class NHLMatchView(MatchView):
    config = ConfigType.nhl


class NHLTeamView(TeamView):
    config = ConfigType.nhl


class NHLCalendarView(CalendarView):
    config = ConfigType.nhl


class NHLCalendarApi(Calendar):
    config = ConfigType.nhl


class NHLUpdateView(UpdateView):
    config = ConfigType.nhl


class NHLUpdateSeasonView(UpdateSeasonView):
    config = ConfigType.nhl

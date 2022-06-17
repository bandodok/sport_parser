from sport_parser.core.configs import ConfigType
from sport_parser.core.views import StatsView, TeamView, MatchView, CalendarView, UpdateView, UpdateSeasonView
from sport_parser.api.views import Calendar


class KHLStatsView(StatsView):
    config = ConfigType.khl


class KHLMatchView(MatchView):
    config = ConfigType.khl


class KHLTeamView(TeamView):
    config = ConfigType.khl


class KHLCalendarView(CalendarView):
    config = ConfigType.khl


class KHLCalendarApi(Calendar):
    config = ConfigType.khl


class KHLUpdateView(UpdateView):
    config = ConfigType.khl


class KHLUpdateSeasonView(UpdateSeasonView):
    config = ConfigType.khl

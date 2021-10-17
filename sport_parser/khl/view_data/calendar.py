from sport_parser.khl.database_services.db_get import get_matches_by_season
from sport_parser.khl.view_data.team_stats import last_matches_info, future_matches_info


def get_calendar_view(season):
    """"""
    matches = get_matches_by_season(season)
    finished_matches = last_matches_info(matches.filter(finished=True).order_by('date')[:50])
    return {
        'season': season,
        'finished_matches': finished_matches,
    }


def get_calendar_finished(season):
    """"""
    matches = get_matches_by_season(season)
    finished_matches = last_matches_info(matches.filter(finished=True).order_by('date')[50:])
    return finished_matches


def get_calendar_unfinished(season):
    """"""
    matches = get_matches_by_season(season)
    unfinished_matches = future_matches_info(matches.filter(finished=False).order_by('date'))
    return unfinished_matches

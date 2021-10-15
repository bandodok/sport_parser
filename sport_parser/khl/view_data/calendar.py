from sport_parser.khl.database_services.db_get import get_matches_by_season
from sport_parser.khl.view_data.team_stats import last_matches_info, future_matches_info


def get_calendar_view(season):
    """"""
    matches = get_matches_by_season(season)
    finished_matches = last_matches_info(matches.filter(finished=True).order_by('date'))
    unfinished_matches = future_matches_info(matches.filter(finished=False).order_by('date'))
    return {
        'finished_matches': finished_matches,
        'unfinished_matches': unfinished_matches,
    }


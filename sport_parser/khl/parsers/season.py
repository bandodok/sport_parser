from django.db import transaction

from sport_parser.khl.database_services.db_add import add_matches_to_database, add_khl_protocol_to_database
from sport_parser.khl.database_services.db_get import get_match_by_id, get_unfinished_matches_id, \
    get_finished_matches_id
from sport_parser.khl.parsers.match_info import get_khl_season_match_info, get_finished_match_info
from sport_parser.khl.parsers.match_protocol import get_khl_protocol


def parse_season(match_list) -> None:
    """Выгружает информацию по всему сезону и добавляет в базу данных"""
    count = 0
    for match in match_list:
        if match == 872325:
            continue
        protocol = get_khl_protocol(match)
        if 'match not found' in protocol:
            count += 1
            if count > 15:
                break
            continue
        with transaction.atomic():
            update_match_status(match)
            add_khl_protocol_to_database(protocol)
        count = 0


def parse_season_matches(season):
    season_match_info = get_khl_season_match_info(season)
    add_matches_to_database(season_match_info)


def update_match_status(match_id):
    info = get_finished_match_info(match_id)
    if info == 'match not updated':
        return
    match = get_match_by_id(match_id)
    match.finished = True
    match.arena = info['arena']
    match.viewers = info['viewers']
    match.save()


def update_protocols(season=0, *, finished=False) -> None:
    """Добавляет недостающие протоколы последнего сезона в базу данных"""
    if finished:
        last_matches_id = get_finished_matches_id(season)
    else:
        last_matches_id = get_unfinished_matches_id()
        season = get_match_by_id(last_matches_id[0]).season.id
    matches_info = get_khl_season_match_info(season, check_finished=False)
    add_matches_to_database(matches_info)
    parse_season(last_matches_id)

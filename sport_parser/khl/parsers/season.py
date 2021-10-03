from django.db import transaction

from sport_parser.khl.database_services.db_add import add_matches_to_database, add_khl_protocol_to_database, \
    last_updated
from sport_parser.khl.database_services.db_get import get_last_match_id, get_match_by_id
from sport_parser.khl.parsers.match_info import get_khl_season_match_info
from sport_parser.khl.parsers.match_protocol import get_khl_protocol


def parse_season(first_match_id) -> None:
    """Выгружает информацию по всему сезону и добавляет в базу данных"""
    count = 0
    for i in range(99999):
        if first_match_id == 872325:
            first_match_id += 1
            continue
        protocol = get_khl_protocol(first_match_id)
        if 'match not found' in protocol:
            count += 1
            first_match_id += 1
            if count > 15:
                break
            continue
        with transaction.atomic():
            update_match_status(first_match_id)
            add_khl_protocol_to_database(protocol)
        count = 0
        first_match_id += 1


def parse_season_matches(season):
    season_match_info = get_khl_season_match_info(season)
    add_matches_to_database(season_match_info)


def update_match_status(match_id):
    match = get_match_by_id(match_id)
    match.finished = True
    match.save()


def update_protocols() -> None:
    """Добавляет недостающие протоколы последнего сезона в базу данных"""
    last_match_id = get_last_match_id()
    if not last_match_id:
        parse_season(55144)
        return
    last_updated(update=True)
    parse_season(last_match_id + 1)
from django.db.models import Max

from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch
from datetime import datetime


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        team = _team_name_update(row['team'])
        season = KHLMatch.objects.get(match_id=row['match_id']).season
        KHLProtocol.objects.create(
            team_id=KHLTeams.objects.filter(season=season).get(name=team).id,
            match_id=KHLMatch.objects.get(match_id=row['match_id']),
            g=row['g'],
            sog=row['sog'],
            penalty=row['penalty'],
            faceoff=row['faceoff'],
            faceoff_p=row['faceoff_p'],
            blocks=row['blocks'],
            hits=row['hits'],
            fop=row['fop'],
            time_a=row['time_a'],
            vvsh=row['vvsh'],
            nshv=row['nshv'],
            pd=row['pd'],
            sh=row['sh']
        )


def add_teams_to_database(team) -> None:
    """Добавляет данные команд в базу данных"""
    KHLTeams.objects.create(
        name=team[0],
        img=team[1],
        city=team[2],
        arena=team[3],
        division=team[4],
        conference=team[5],
        season=team[6]
        )


def add_matches_to_database(match):
    """Добавляет информацию о матчах в базу данных"""
    KHLMatch.objects.create(
        match_id=match[0],
        match_date=match[1],
        season=match[2],
        arena=match[3],
        city=match[4],
        viewers=match[5]
    )


def _team_name_update(team):
    if team == 'Торпедо НН':
        new_team = 'Торпедо'
    elif team == 'Динамо Мск':
        new_team = 'Динамо М'
    elif team == 'ХК Динамо М':
        new_team = 'Динамо М'
    else:
        return team
    return new_team


def last_updated(*, update=False):
    """Возвращает дату последнего обновления таблицы матчей
    При update=True обновляет эту дату на текущую"""
    last_update = KHLMatch.objects.aggregate(Max('updated'))['updated__max']
    if update:
        last = KHLMatch.objects.get(updated=last_update)
        last.updated = datetime.now()
        last.save()
    return last_update

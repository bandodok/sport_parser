from django.db import transaction
from django.db.models import Max

from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch
from datetime import datetime


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        team = _team_name_update(row[0])
        season = KHLMatch.objects.get(match_id=row[1]).season
        KHLProtocol.objects.create(
            team_id=KHLTeams.objects.filter(season=season).get(name=team).id,
            match_id=KHLMatch.objects.get(match_id=row[1]),
            g=row[2],
            sog=row[3],
            penalty=row[4],
            faceoff=row[5],
            faceoff_p=row[6],
            blocks=row[7],
            hits=row[8],
            fop=row[9],
            time_a=row[10],
            vvsh=row[11],
            nshv=row[12],
            pd=row[13],
            sh=row[14]
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


def add_matches_to_database(matches):
    """Добавляет информацию о матчах в базу данных"""
    for match in matches:
        with transaction.atomic():
            a, _ = KHLMatch.objects.get_or_create(
                match_id=match['match_id'],
            )
            a.date = match['date']
            a.time = match['time']
            a.season = match['season']
            a.city = match['city']
            a.arena = match['arena']
            a.finished = match['finished']
            a.viewers = match['viewers']
            a.save()
            home_team = KHLTeams.objects.filter(season=match['season']).get(name=match['home_team'])
            guest_team = KHLTeams.objects.filter(season=match['season']).get(name=match['guest_team'])
            a.teams.add(home_team, guest_team)
            a.save()


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

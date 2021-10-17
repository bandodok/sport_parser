from django.db import transaction
from django.db.models import Max

from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch
from datetime import datetime


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        team = _team_name_update(row['team'])
        season = KHLMatch.objects.get(match_id=row['match_id']).season
        p, _ = KHLProtocol.objects.get_or_create(
            team_id=KHLTeams.objects.filter(season=season).get(name=team),
            match_id=KHLMatch.objects.get(match_id=row['match_id'])
        )
        p.g = row.get('g', '0')
        p.sog = row.get('sog', '0')
        p.penalty = row.get('penalty', '0')
        p.faceoff = row.get('faceoff', '0')
        p.faceoff_p = row.get('faceoff_p', '00:00')
        p.blocks = row.get('blocks', '0')
        p.hits = row.get('hits', '0')
        p.fop = row.get('fop', '0')
        p.time_a = row.get('time_a', '00:00:00')
        p.vvsh = row.get('vvsh', '00:00:00')
        p.nshv = row.get('nshv', '00:00:00')
        p.pd = row.get('pd', '00.00')
        p.sh = row.get('sh', 0)
        p.save()


def add_teams_to_database(team_info) -> None:
    """Добавляет данные команд в базу данных"""
    team_name = _team_name_update(team_info[0])
    team, _ = KHLTeams.objects.get_or_create(name=team_name, season=team_info[6])
    team.img = team_info[1]
    team.city = team_info[2]
    team.arena = team_info[3]
    team.division = team_info[4]
    team.conference = team_info[5]
    team.save()


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
            home_team = _team_name_update(match['home_team'])
            guest_team = _team_name_update(match['guest_team'])
            home_team = KHLTeams.objects.filter(season=match['season']).get(name=home_team)
            guest_team = KHLTeams.objects.filter(season=match['season']).get(name=guest_team)
            a.teams.add(home_team, guest_team)
            a.save()


def _team_name_update(team):
    if team == 'Торпедо НН':
        new_team = 'Торпедо'
    elif team == 'Динамо Мск':
        new_team = 'Динамо М'
    elif team == 'ХК Динамо М':
        new_team = 'Динамо М'
    elif team == 'ХК Сочи':
        new_team = 'Сочи'
    else:
        return team
    return new_team


def last_updated(*, update=False):
    """Возвращает дату последнего обновления таблицы матчей
    При update=True обновляет эту дату на текущую"""
    last_update = KHLMatch.objects.aggregate(Max('updated'))['updated__max']
    if update:
        last_matches = KHLMatch.objects.filter(updated=last_update)
        last = last_matches[len(last_matches) - 1]
        last.updated = datetime.now()
        last.save()
    return last_update

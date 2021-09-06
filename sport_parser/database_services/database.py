from sport_parser.khl.models import KHLProtocol, KHLTeams, KHLMatch
from django.db.models import Sum
import datetime


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        team = row[0]
        if row[0] == 'Торпедо НН':
            team = 'Торпедо'
        if row[0] == 'Динамо Мск':
            team = 'Динамо М'
        if row[0] == 'ХК Динамо М':
            team = 'Динамо М'
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


def get_team_stats_view(season):
    """Возвращает список с рассчитанной статистикой команд в виде списков"""
    stats = [[
        'Team',
        'Sh',
        'Sh(A)',
        'Sh%',
        'SoG',
        'SoG(A)',
        'AQ',
        'G',
        'G(A)',
        'FaceOff%',
        'TimeA',
        'TimeA(A)',
        'TimeA%',
        'DEV%',
        'PDO%',
        'Hits',
        'Blocks',
        'Blocks(A)',
        'Blocks%',
        'Penalty',

    ]]
    teams = get_team_list(season)
    for team in teams:
        team_stats = [get_team_name(team), ]
        match_list = get_match_list(team)

        sh = get_team_stat(team, 'sh', match_list, mode='median')
        sog = get_team_stat(team, 'sog', match_list, mode='median')
        g = get_team_stat(team, 'g', match_list, mode='median')
        blocks = get_team_stat(team, 'blocks', match_list, mode='median')
        time_a = get_team_stat(team, 'time_a', match_list, mode='median')
        penalty = get_team_stat(team, 'penalty', match_list, mode='median')
        hits = get_team_stat(team, 'hits', match_list, mode='median')

        sha = get_opponent_stat(team, 'sh', match_list, mode='median')
        soga = get_opponent_stat(team, 'sog', match_list, mode='median')
        ga = get_opponent_stat(team, 'g', match_list, mode='median')
        blocksa = get_opponent_stat(team, 'blocks', match_list, mode='median')
        time_aa = get_opponent_stat(team, 'time_a', match_list, mode='median')

        faceoff = get_team_stat(team, 'faceoff', match_list, mode='sum')
        faceoffa = get_opponent_stat(team, 'faceoff', match_list, mode='sum')

        shp = f'{format(sh / (sh + sha) * 100, ".2f")}%'
        sogp = f'{format(sog / sh * 100, ".2f")}%'
        faceoffp = f'{format(faceoff / (faceoff + faceoffa) * 100, ".2f")}%'
        blocksp = f'{format(blocks / (blocks + blocksa) * 100, ".2f")}%'
        devp = f'{format((1 - (soga / sha)) * 100, ".2f")}%'
        time_ap = f'{format(time_a / (time_a + time_aa) * 100, ".2f")}%'

        pdo = f'{format(((sh / (sh + sha)) + (sog / sh)) * 100, ".2f")}%'

        time_a = sec_to_time(time_a)
        time_aa = sec_to_time(time_aa)

        formated_stats = output_format([
            sh, sha, shp, sog, soga,
            sogp, g, ga, faceoffp,
            time_a, time_aa, time_ap,
            devp, pdo, hits, blocks,
            blocksa, blocksp, penalty
        ])

        team_stats.extend(formated_stats)

        stats.append(team_stats)

    return stats


def get_team_list(season):
    """Возвращает список id команд, отсортированный по названию команд"""
    teams = KHLTeams.objects.filter(season=season).order_by('name').values('id')
    return [team['id'] for team in teams]


def get_match_list(team):
    """Возвращает список матчей match_id команды team"""
    match_list = KHLProtocol.objects.filter(team_id=team).values_list('match_id')
    return [match[0] for match in match_list]


def get_team_stat(team, stat, match_list, *, mode='median'):
    """В зависимости от mode возвращает медиану или сумму параметра stat команды team в матчах match_list
    mode:
        median - рассчитать медиану
        sum - рассчитать сумму
    """
    stat_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=team).order_by(stat)
    return _calculate_stat(stat, stat_list, mode=mode)


def get_opponent_stat(team, stat, match_list, *, mode='median'):
    """В зависимости от mode возвращает медиану или сумму параметра stat противника команды team в матчах match_list
    mode:
        median - рассчитать медиану
        sum - рассчитать сумму
    """
    stat_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=team).order_by(stat)
    return _calculate_stat(stat, stat_list, mode=mode)


def _calculate_stat(stat, stat_list, mode='median'):
    if mode == 'median':
        return get_median(stat_list.values_list(stat))
    if mode == 'sum':
        calc_stat = stat_list.aggregate(Sum(stat))
        return calc_stat[f'{stat}__sum']
    raise ValueError('Invalid mode')


def get_median(item_list):
    """Возвращает медиану списка"""
    items = [x[0] for x in item_list]
    if len(items) % 2 != 0:
        median = int(len(items) // 2)
        if type(items[median]) == datetime.time:
            return round(time_to_sec(items[median]), 0)
        return items[median]
    median = int(len(items) / 2)
    if type(items[median]) == datetime.time:
        time1 = time_to_sec(items[median])
        time2 = time_to_sec(items[median - 1])
        return round((time1 + time2) / 2, 0)
    return (items[median] + items[median - 1]) / 2


def time_to_sec(time):
    """Возвращает время в секундах"""
    return time.hour * 3600 + time.minute * 60 + time.second


def sec_to_time(time):
    """Возвращает время в виде строки в формате HH:MM"""
    min = int(time // 60)
    sec = int(time - min * 60)
    if sec < 10:
        sec = f'0{sec}'
    return f'{min}:{sec}'


def output_format(items):
    """Принимает список значений и возвращает отформатированный для вывода список"""
    out = []
    for item in items:
        if type(item) == str:
            out.append(item)
            continue
        out.append(format(item, ".1f"))
    return out


def get_team_name(team_id):
    """Возвращает название команды по id"""
    return KHLTeams.objects.get(id=team_id).name

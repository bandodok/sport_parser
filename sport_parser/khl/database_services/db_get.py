import datetime

from django.db.models import Sum, Max

from sport_parser.khl.models import KHLMatch, KHLTeams, KHLProtocol


def get_team_list(season):
    """Возвращает список id команд в сезоне, отсортированный по названию команд"""
    teams = KHLTeams.objects.filter(season=season).order_by('name').values('id')
    return [team['id'] for team in teams]


def get_match_list(team):
    """Возвращает список матчей match_id команды team"""
    match_list = KHLProtocol.objects.filter(team_id=team).values_list('match_id')
    return [match[0] for match in match_list]


def get_team_stat(team, stat, match_list, *, mode='list'):
    """В зависимости от mode возвращает медиану или сумму параметра stat команды team в матчах match_list
    mode:
        median - рассчитать медиану
        sum - рассчитать сумму
        list - список
    """
    if mode == 'list':
        queryset = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=team).values_list(stat, flat=True)
        return [v for v in queryset]
    stat_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=team).order_by(stat)
    return _calculate_stat(stat, stat_list, mode=mode)


def get_opponent_stat(team, stat, match_list, *, mode='median'):
    """В зависимости от mode возвращает медиану или сумму параметра stat противника команды team в матчах match_list
    mode:
        median - рассчитать медиану
        sum - рассчитать сумму
        list - список
    """
    if mode == 'list':
        queryset = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=team).values_list(stat, flat=True)
        return [v for v in queryset]
    stat_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=team).order_by(stat)
    return _calculate_stat(stat, stat_list, mode=mode)


def get_team_stats_per_day(team, *args):
    match_list = get_match_list(team)
    query = KHLProtocol.objects.filter(match_id__in=match_list)
    out = query.filter(team_id=team).values_list(*args)
    return [[stat for stat in day] for day in out]


def get_opp_stats_per_day(team, *args):
    match_list = get_match_list(team)
    query = KHLProtocol.objects.filter(match_id__in=match_list)
    out = query.exclude(team_id=team).values_list(*args)
    return [[stat for stat in day] for day in out]


def _calculate_stat(stat, stat_list, mode='list'):
    if mode == 'median':
        stats = stat_list.values_list(stat, flat=True)
        return get_median([x for x in stats])
    if mode == 'sum':
        calc_stat = stat_list.aggregate(Sum(stat))
        return calc_stat[f'{stat}__sum']
    raise ValueError('Invalid mode')


def get_median(items):
    """Возвращает медиану списка"""
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


def get_team_attr(team_id, attr):
    """Возвращает атрибут команды по id"""
    return KHLTeams.objects.filter(id=team_id).values_list(attr, flat=True)[0]


def get_team_id_by_season(team_id):
    """Возвращает список id команды для разных сезонов"""
    name = KHLTeams.objects.get(id=team_id).name
    season_list = KHLTeams.objects.filter(name=name).order_by('season').values('id', 'season')
    return [x for x in season_list]


def get_last_match_id():
    """Возвращает id последнего матча в базе данных"""
    return KHLMatch.objects.filter(finished=True).aggregate(Max('match_id'))['match_id__max']


def get_match_by_id(match_id):
    """ """
    return KHLMatch.objects.get(match_id=match_id)


def get_team_by_id(team_id):
    """ """
    return KHLTeams.objects.get(id=team_id)


def get_unfinished_matches_id():
    """Возвращает список id незавершенных матчей"""
    return KHLMatch.objects.filter(finished=False).order_by('date').values_list('match_id', flat=True)


def get_team_season_stats(team):
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

    return formated_stats


def get_match_stats(match_id):
    match = get_match_by_id(match_id)
    team1, team2 = match.teams.all()
    p1 = match.khlprotocol_set.all().get(team_id=team1.id)
    p2 = match.khlprotocol_set.all().get(team_id=team2.id)

    match_stats = [
        [
            'Team_id',
            'Team',
            'Sh',
            'SoG',
            'G',
            'FaceOff',
            'FaceOff%',
            'Hits',
            'Blocks',
            'Penalty',
            'TimeA',
        ],
    ]

    team1_stats = [
        p1.team_id.id,
        p1.team_id.name,
    ]

    team2_stats = [
        p2.team_id.id,
        p2.team_id.name,
    ]

    team1_stats.extend(output_format(
        [p1.sh, p1.sog, p1.g, p1.faceoff, p1.faceoff_p, p1.hits, p1.blocks, p1.penalty, sec_to_time(time_to_sec(p1.time_a))]))

    team2_stats.extend(output_format(
        [p2.sh, p2.sog, p2.g, p2.faceoff, p2.faceoff_p, p2.hits, p2.blocks, p2.penalty, sec_to_time(time_to_sec(p2.time_a))]))

    match_stats.extend([team1_stats, team2_stats])

    return match_stats

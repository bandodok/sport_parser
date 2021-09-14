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


def _calculate_stat(stat, stat_list, mode='list'):
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


def get_last_match_id():
    """Возвращает id последнего матча в базе данных"""
    return KHLMatch.objects.aggregate(Max('match_id'))['match_id__max']

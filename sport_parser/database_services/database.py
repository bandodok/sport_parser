from sport_parser.khl.models import KHLProtocol
from django.db.models import Sum
import time, datetime


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        KHLProtocol.objects.create(
            team_id=row[0],
            match_id=row[1],
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


def get_team_stats_view():
    """Возвращает список с рассчитанной статистикой команд в виде списков"""
    stats = [[
        'Club',
        'Sh',
        'Sh(A)',
        'Sh%',
        'SoG',
        'SoG(A)',
        'AQ',
        'G',
        'G(A)',
        'FaceOff%',
        'Blocks',
        'Blocks(A)',
        'Blocks%',
        'DEV%',
        'TimeA',
        'TimeA(A)',
        'TimeA%',
        'Penalty',
        'Hits',
    ]]
    teams = KHLProtocol.objects.values('team_id').order_by('team_id').distinct()
    for team in teams:
        t = team['team_id']
        team_stats = [t, ]
        match_list = KHLProtocol.objects.filter(team_id=t).values_list('match_id')

        sh_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('sh')
        sh = get_median(sh_list)
        team_stats.append(format(sh, ".1f"))

        sha_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).values_list('sh')
        sha = get_median(sha_list)
        team_stats.append(format(sha, ".1f"))

        shp = f'{format(sh / (sh + sha) * 100, ".2f")}%'
        team_stats.append(shp)

        sog_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('sog')
        sog = get_median(sog_list)
        team_stats.append(format(sog, ".1f"))

        soga_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).values_list('sog')
        soga = get_median(soga_list)
        team_stats.append(format(soga, ".1f"))

        sogp = f'{format(sog * 100 / sh, ".2f")}%'
        team_stats.append(sogp)

        g_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('g')
        g = get_median(g_list)
        team_stats.append(format(g, ".1f"))

        ga_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).values_list('g')
        ga = get_median(ga_list)
        team_stats.append(format(ga, ".1f"))

        faceoff = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).aggregate(Sum('faceoff'))
        faceoff = faceoff['faceoff__sum']

        faceoffa = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).aggregate(Sum('faceoff'))
        faceoffa = faceoffa['faceoff__sum']

        faceoffp = f'{format(faceoff / (faceoff + faceoffa) * 100, ".2f")}%'
        team_stats.append(faceoffp)

        blocks_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('blocks')
        blocks = get_median(blocks_list)
        team_stats.append(format(blocks, ".1f"))

        blocksa_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).values_list('blocks')
        blocksa = get_median(blocksa_list)
        team_stats.append(format(blocksa, ".1f"))

        blocksp = f'{round(blocks / (blocks + blocksa) * 100, 2)}%'
        team_stats.append(blocksp)

        devp = f'{format((1 - (soga / sha)) * 100, ".2f")}%'
        team_stats.append(devp)

        time_a_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('time_a')
        time_a = get_median(time_a_list)
        team_stats.append(sec_to_time(time_a))

        time_aa_list = KHLProtocol.objects.filter(match_id__in=match_list).exclude(team_id=t).values_list('time_a')
        time_aa = get_median(time_aa_list)
        team_stats.append(sec_to_time(time_aa))

        time_ap = f'{format(time_a / (time_a + time_aa) * 100, ".2f")}%'
        team_stats.append(time_ap)

        penalty_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('penalty')
        penalty = get_median(penalty_list)
        team_stats.append(format(penalty, ".1f"))

        hits_list = KHLProtocol.objects.filter(match_id__in=match_list).filter(team_id=t).values_list('hits')
        hits = get_median(hits_list)
        team_stats.append(format(hits, ".1f"))

        stats.append(team_stats)

    return stats


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
    return time.hour * 3600 + time.minute * 60 + time.second


def sec_to_time(time):
    min = int(time // 60)
    sec = int(time - min * 60)
    if sec < 10:
        sec = f'0{sec}'
    return f'{min}:{sec}'

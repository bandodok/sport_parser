import requests
import functools
from django.conf import settings
from django.db import transaction
import pandas as pd
from bs4 import BeautifulSoup
from sport_parser.database_services.database import add_khl_protocol_to_database, add_teams_to_database, \
    add_matches_to_database
from sport_parser.khl.models import KHLMatch
from django.db.models import Max


def get_score_table():
    """корректно работает на вкладке stats, не работает в standings"""
    url = 'https://www.khl.ru/stat/teams/1045/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    column_tags = soup.find('thead')
    columns = column_tags.find_all('th')
    columns = [x.text for x in columns]

    rows = []
    a = soup.find_all('tr')
    b = [x for x in a if x.find_all(class_='e-club_name')]
    for v in b:
        tr = v.find_all('td')
        stats = [td.text.strip() for td in tr]
        rows.append(stats)

    total_team_stats = pd.DataFrame(rows, columns=columns)
    return total_team_stats


@functools.lru_cache(maxsize=5)
def _get_request_content(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')


def get_khl_match_info(match_id):
    """ """
    url = f"https://text.khl.ru/text/{match_id}.html"
    soup = _get_request_content(url)

    team_info = soup.find('div', class_='b-content_section m-match_info').find_all('span')
    datetime = str(team_info[2]).split('<br/>')
    time = datetime[1][:-7]
    date = datetime[0][6:].split(' ')[::-1]
    month = month_to_int_replace(date[1])
    full_date = f'{date[0]}-{month}-{date[2]} {time}'

    arena_viewers = team_info[4]
    viewers = str(arena_viewers).split('<br/>')[1].split(' ')[0]
    if viewers == '</span>':
        viewers = 0
    arena_city = str(arena_viewers).split('<br/>')[0][6:].split('(')
    arena = arena_city[0].strip()
    city = arena_city[1][:-1]

    season = 0
    for s, id in settings.SEASONS_FIRST_MATCH.items():
        if id <= match_id:
            season = s
            break
    return [match_id, full_date, season, arena, city, viewers]


def month_to_int_replace(month: str):
    """Возвращает номер месяца по слову"""
    months = {
        'янв.': '01',
        'февр.': '02',
        'марта': '03',
        'авг.': '08',
        'сент.': '09',
        'окт.': '10',
        'нояб.': '11',
        'дек.': '12'
    }
    return months.get(month)


def get_khl_protocol(match_id):
    """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
    url = f"https://text.khl.ru/text/{match_id}.html"
    soup = _get_request_content(url)
    team_stats = soup.find_all('div', class_="table-responsive")
    if not team_stats:
        return f'match not found {match_id}'

    # Общего количества бросков нет в протоколе, берется отдельно из текстовой трансляции
    text_stats = soup.find_all('p', class_='e-action_txt')
    team_stats_row = [x for x in text_stats if 'Статистика матча:' in x.text or 'Game stats:' in x.text]
    if team_stats_row:
        team_stats_row = team_stats_row[0].text
        sh_home = team_stats_row.split(':')[2].split('-')[0].strip()
        sh_guest = team_stats_row.split(':')[2].split('-')[1].split(' ')[0]
    # Если в тексте нет отчета по игре, броски складываются из отчетов по периодам
    else:
        p1 = [x for x in text_stats if 'Stats of 1st period:' in x.text or 'Статистика 1-го периода:' in x.text][0].text
        p1_home = p1.split(':')[2].split('-')[0].strip()
        p1_guest = p1.split(':')[2].split('-')[1].split(' ')[0]
        p2 = [x for x in text_stats if 'Stats of 2nd period:' in x.text or 'Статистика 2-го периода:' in x.text][0].text
        p2_home = p2.split(':')[2].split('-')[0].strip()
        p2_guest = p2.split(':')[2].split('-')[1].split(' ')[0]
        p3 = [x for x in text_stats if 'Stats of 3rd period:' in x.text or 'Статистика 3-го периода:' in x.text][0].text
        p3_home = p3.split(':')[2].split('-')[0].strip()
        p3_guest = p3.split(':')[2].split('-')[1].split(' ')[0]
        p4 = [x for x in text_stats if 'Stats of overtime:' in x.text or 'Статистика овертайма:' in x.text]
        p4_home = 0
        p4_guest = 0
        if p4:
            p4 = p4[0].text
            p4_home = p4.split(':')[2].split('-')[0].strip()
            p4_guest = p4.split(':')[2].split('-')[1].split(' ')[0]

        sh_home = int(p1_home) + int(p2_home) + int(p3_home) + int(p4_home)
        sh_guest = int(p1_guest) + int(p2_guest) + int(p3_guest) + int(p4_guest)

    head = [x.find_all('th') for x in team_stats][0]
    body = [x.find_all('td') for x in team_stats][0]
    columns = [i.text.strip() for i in head]
    rows = [i.text.strip() for i in body]

    # находим индекс объединенной ячейки чтобы дублировать его во вторую строку
    rowspan = {body.index(i): i.text.strip() for i in body if i.attrs == {'rowspan': '2'}}
    for k, v in rowspan.items():
        len_ = int((len(rows) + 1) / 2)
        rows.insert((k + len_), v)

    row_len = int(len(rows) / 2)
    row_home = rows[:row_len]
    row_home.insert(1, match_id)
    row_home = row_update_type(row_home)
    row_home.append(str(sh_home))
    row_guest = rows[row_len:]
    row_guest.insert(1, match_id)
    row_guest = row_update_type(row_guest)
    row_guest.append(str(sh_guest))
    return row_home, row_guest


def row_update_type(row):
    """Приводит некорректные типы данных в протоколах к корректному
    для восприятия базой данных"""
    for stat in row[2:]:
        if not stat:
            row[row.index(stat)] = 0
            continue
        if ':' in stat:
            row[row.index(stat)] = f'00:{stat}'
    if 14 - len(row) != 0:
        for _ in range(14 - len(row)):
            row.append(0)
    return row


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
        match_info = get_khl_match_info(first_match_id)
        with transaction.atomic():
            add_matches_to_database(match_info)
            add_khl_protocol_to_database(protocol)
        count = 0
        first_match_id += 1


def update_protocols() -> None:
    """Добавляет недостающие протоколы последнего сезона в базу данных"""
    last_match_id = KHLMatch.objects.aggregate(Max('match_id'))['match_id__max']
    if not last_match_id:
        last_match_id = 55143
    parse_season(last_match_id + 1)


def parse_teams():
    teams = []
    for season in settings.SEASONS.values():
        season_teams = parse_teams_in_season(season)
        teams.extend([team for team in season_teams])
    for team in teams:
        add_teams_to_database(team)


def parse_teams_in_season(season_id):
    url = f'https://www.khl.ru/standings/{season_id}/division/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    divisions = soup.find('div', id='tab-standings-division').find_all('div', class_='k-data_table')
    teams = []

    season = 0
    for s, id in settings.SEASONS.items():
        if id <= season_id:
            season = s
            break

    # Дивизион Боброва
    division_soup = divisions[0].find_all('a')
    division = 'Боброва'
    conference = 'Запад'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Тарасова
    division_soup = divisions[1].find_all('a')
    division = 'Тарасова'
    conference = 'Запад'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Харламова
    division_soup = divisions[2].find_all('a')
    division = 'Харламова'
    conference = 'Восток'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    # Дивизион Чернышева
    division_soup = divisions[3].find_all('a')
    division = 'Чернышева'
    conference = 'Восток'
    teams.extend(_get_division_team_list(division_soup, division, conference, season))

    return teams


def _get_division_team_list(division_soup, division, conference, season):
    """Возвращает """
    teams = []
    for i in division_soup:
        team_src = f"https://www.khl.ru{i['href']}arena/"
        r = requests.get(team_src)
        soup = BeautifulSoup(r.content, 'html.parser')
        city_table = soup.find('div', class_='b-blocks_cover')

        name = i.text
        img = f"https://www.khl.ru{city_table.find('img')['src']}"
        city = city_table.find('p').text
        arena = soup.find_all('div', class_='b-short_block').pop().find('h4').text

        teams.append([name, img, city, arena, division, conference, season])

    return teams

import requests
import pandas as pd
from bs4 import BeautifulSoup
from sport_parser.database_services.database import add_khl_protocol_to_database


def get_teams():
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


def get_khl_protocol(match_id):
    """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
    url1 = f"https://text.khl.ru/text/{match_id}.html"
    r = requests.get(url1)
    soup = BeautifulSoup(r.content, 'html.parser')
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
        p4 = [x for x in text_stats if 'Stats of overtime:' in x.text or 'Статистика овертайма:' in x.text][0].text
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
    row_home.append(str(sh_home))
    row_home = row_update_type(row_home)
    row_guest = rows[row_len:]
    row_guest.insert(1, match_id)
    row_guest.append(str(sh_guest))
    row_guest = row_update_type(row_guest)
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
    if 15 - len(row) != 0:
        for _ in range(15 - len(row)):
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
        add_khl_protocol_to_database(protocol)
        first_match_id += 1


# start = 872319
# end = 873008

from django.conf import settings

from sport_parser.khl.parsers.request import get_selenium_content, get_request_content


def get_khl_season_match_info(season, webdriver=get_selenium_content, check_finished=True):
    s = settings.SEASONS.get(str(season), 0)
    if s == 0:
        return f'season {s} not found'

    output = []

    url = f'https://www.khl.ru/calendar/{s}/00/'
    soup = webdriver(url)
    match_soup = soup.find('div', id='tab-calendar-all')
    if not match_soup:
        match_soup = soup.find('div', id='tab-calendar-last')

    dates = match_soup.find_all('div', class_='b-final_cup_date')
    dates = [date.b.text for date in dates]

    matches = match_soup.find_all('div', class_='m-future')
    match_dict = {date: match_soup for date, match_soup in zip(dates, matches)}
    for date, matches in match_dict.items():
        match_list = matches.find_all('li', class_='b-wide_tile_item')
        new_date = _date_format(date)
        for match in match_list:
            href = match.find('dl', class_='b-title-option').div.div.ul.li.a['href']
            match_id = href.split('/')[3]
            # у матчей дивизиона нет ссылок на страницу команды
            home_team_a = match.find('dl', class_='b-details m-club').dd.h5.a
            if not home_team_a:
                continue
            home_team = home_team_a.text
            guest_team = match.find('dl', class_='b-details m-club m-rightward').dd.h5.a.text
            score = match.find('dl', class_='b-score')
            if '—' in score.dt.h3.text:
                finished = True
                if not check_finished:
                    continue
                match_info = get_finished_match_info(match_id)
                if match_info == 'match not updated':
                    continue
            else:
                finished = False
                time = score.dt.h3.text.split(' ')[0]
                city = score.dd.p.text
                match_info = {
                    'arena': '',
                    'city': city,
                    'time': time,
                    'viewers': 0,
                    'penalties': False,
                    'overtime': False
                }
            match_info.update({
                'finished': finished,
                'match_id': match_id,
                'date': new_date,
                'home_team': home_team,
                'guest_team': guest_team,
                'season': season
            })
            output.append(match_info)
    return output


def get_finished_match_info(match_id):
    url = f'https://text.khl.ru/text/{match_id}.html'
    soup = get_request_content(url)

    extra_info = soup.find_all('li', class_="b-match_add_info_item")
    if not extra_info:
        return 'match not updated'

    match_status = soup.find('dd', class_="b-period_score").text
    if match_status != 'матч завершен':
        return 'match not updated'

    penalties = False
    overtime = False
    score_status = soup.find('dt', class_="b-total_score").h3
    if 'Б' in score_status.text:
        penalties = True
    if 'ОТ' in score_status.text:
        overtime = True

    date_info = extra_info[0]
    arena_info = extra_info[1]

    info = date_info.find_all('span')[1]
    info = str(info).split('<br/>')
    time = info[1][:5]

    info = arena_info.find_all('span')[1]

    info = str(info).split('<br/>')
    arena_city = info[0][6:]
    arena, city = arena_city.split('(')
    arena = arena[:-1]
    city = city[:-1]
    city = city.strip()

    if info[1] == '</span>':
        viewers = 0
    else:
        viewers = info[1][:-16]

    return {
        'arena': arena,
        'city': city,
        'time': time,
        'viewers': viewers,
        'penalties': penalties,
        'overtime': overtime
    }


def _date_format(date):
    splitted_date = date.split(' ')[:-1]
    if not splitted_date[0]:
        splitted_date.pop(0)
    day, month, year = splitted_date
    if len(day) == 1:
        day = f'0{day}'
    month = month_to_int_replace(month)
    year = year[:-1]
    return f'{year}-{month}-{day}'


def month_to_int_replace(month: str):
    """Возвращает номер месяца по слову"""
    months = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12'
    }
    return months.get(month)

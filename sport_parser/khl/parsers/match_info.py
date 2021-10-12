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
            home_team = match.find('dl', class_='b-details m-club').dd.h5.a.text
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
                arena = ''
                viewers = 0
                match_info = {
                    'arena': arena,
                    'city': city,
                    'time': time,
                    'viewers': viewers
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
    season = 0
    for s, id in settings.SEASONS_FIRST_MATCH.items():
        if id <= int(match_id):
            season = settings.SEASONS.get(s)
            break

    url = f'https://www.khl.ru/game/{season}/{match_id}/preview/'
    soup = get_request_content(url)
    extra_info = soup.find_all('li', class_="b-match_add_info_item")

    # если матч завершился, но страницу еще не обновили, прерываем обновление чтобы обновить позже
    if not extra_info:
        return 'match not updated'

    date_info = extra_info[0]
    arena_info = extra_info[1]

    info = date_info.find_all('span')[1]
    info = str(info).split('<br/>')
    time = info[1][:5]

    info = arena_info.find_all('span')[1]

    info = str(info).split('<br/>')
    arena_city = info[0][6:]
    arena, city = arena_city.split(',')
    viewers = info[1][:-16]
    city = city.strip()
    return {
        'arena': arena,
        'city': city,
        'time': time,
        'viewers': viewers
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

from django.conf import settings

from sport_parser.khl.parsers.request import get_request_content


def get_khl_match_info(match_id):
    """ """
    url = f"https://text.khl.ru/text/{match_id}.html"
    soup = get_request_content(url)

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

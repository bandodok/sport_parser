from bs4 import BeautifulSoup

from sport_parser.khl.parsers.match_info import get_khl_match_info, month_to_int_replace


def fake_webdriver(url):
    if url == 'https://www.khl.ru/game/1097/877200/preview/':
        r = open('tests/fixtures/team_info_finished.html', encoding='utf-8').read()
        return BeautifulSoup(r, 'html.parser')
    if url == 'https://www.khl.ru/game/1097/877300/preview/':
        r = open('tests/fixtures/team_info_unfinished.html', encoding='utf-8').read()
        return BeautifulSoup(r, 'html.parser')


def test_month_to_int_replace():
    assert month_to_int_replace('янв.') == '01'
    assert month_to_int_replace('марта') == '03'
    assert month_to_int_replace('дек.') == '12'


def test_get_khl_match_info():
    info = get_khl_match_info(877200, webdriver=fake_webdriver)
    info1 = get_khl_match_info(877300, webdriver=fake_webdriver)

    out_info = {
        'match_id': 877200,
        'date': '2021-09-09 19:30',
        'season': '21',
        'arena': 'МУП «Арена «Мытищи»',
        'city': 'Мытищи',
        'finished': True
    }
    out_info1 = {
        'match_id': 877300,
        'date': '2021-10-01 17:00',
        'season': '21',
        'arena': 'УКРК «Арена Металлург»',
        'city': 'Магнитогорск',
        'finished': False
    }

    assert info == out_info
    assert info1 == out_info1

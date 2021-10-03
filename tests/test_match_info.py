import pook
import pytest
from bs4 import BeautifulSoup

from sport_parser.khl.parsers.match_info import get_khl_season_match_info, month_to_int_replace, get_finished_match_info


@pytest.fixture
def get_match_info_finished():
    return open('tests/fixtures/team_info_finished.html', encoding='utf-8').read()


def fake_webdriver(url):
    if url == 'https://www.khl.ru/calendar/1097/00/':
        r = open('tests/fixtures/calendar.html', encoding='utf-8').read()
        return BeautifulSoup(r, 'html.parser')


def test_month_to_int_replace():
    assert month_to_int_replace('января') == '01'
    assert month_to_int_replace('марта') == '03'
    assert month_to_int_replace('декабря') == '12'


@pook.on
def test_get_khl_season_match_info(get_match_info_finished):
    mock = pook.get('https://www.khl.ru/game/1097/877200/preview/',
                    reply=200,
                    response_body=get_match_info_finished
                    )
    info = get_khl_season_match_info(21, webdriver=fake_webdriver)

    out_info = [
        {'arena': 'МУП «Арена «Мытищи»',
         'city': 'Мытищи',
         'date': '2021-09-09',
         'finished': True,
         'guest_team': 'Йокерит',
         'home_team': 'Куньлунь РС',
         'match_id': '877200',
         'season': 21,
         'time': '19:30',
         'viewers': '253'},
        {'arena': '',
         'city': 'Магнитогорск',
         'date': '2021-10-01',
         'finished': False,
         'guest_team': 'Автомобилист',
         'home_team': 'Металлург Мг',
         'match_id': '877300',
         'season': 21,
         'time': '17:00',
         'viewers': 0}
    ]

    assert mock.calls == 1
    assert info == out_info


@pook.on
def test_get_finished_match_info(get_match_info_finished):
    info = get_finished_match_info(877200)

    out_info = {
        'arena': 'МУП «Арена «Мытищи»',
        'city': 'Мытищи',
        'time': '19:30',
        'viewers': '253'
    }

    assert info == out_info

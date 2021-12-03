import pook
import pytest
from sport_parser.khl.models import KHLSeason, KHLMatch
from sport_parser.khl.data_taking.parser import Parser
from fixtures.db_fixture import update_db


@pytest.fixture
def get_match_info_finished():
    return open('tests/fixtures/team_info_finished.html', encoding='utf-8').read()


@pytest.fixture
def get_calendar():
    return open('tests/fixtures/calendar.html', encoding='utf-8').read()


@pytest.fixture()
def get_teams_html():
    return open('tests/fixtures/teams.html', encoding='utf-8').read()


@pytest.fixture
def get_protocol():
    return open('tests/fixtures/protocol.html', encoding='utf-8').read()


@pytest.fixture
def get_protocol1():
    return open('tests/fixtures/protocol1.html', encoding='utf-8').read()


@pytest.fixture()
def get_teams():
    teams = []
    with open('tests/fixtures/teams/team1.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team2.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team3.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team4.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team5.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team6.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team7.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/teams/team8.html', encoding='utf-8') as f:
        teams.append(f.read())
    return teams


@pytest.mark.django_db(transaction=True)
@pook.on
def test_parse_calendar(update_db, get_calendar, get_match_info_finished):
    mock = pook.get('https://www.khl.ru/calendar/1097/00/',
                    reply=200,
                    response_body=get_calendar
                    )
    parser = Parser()
    season = KHLSeason.objects.get(id=21)
    info = parser.parse_calendar(season)

    out_info = [
        {'date': '2021-09-09',
         'finished': True,
         'guest_team': 'Йокерит',
         'home_team': 'Куньлунь РС',
         'match_id': '877200',
         'season': season,
         'overtime': False,
         'penalties': False,
         },
        {'city': 'Магнитогорск',
         'date': '2021-10-01',
         'finished': False,
         'guest_team': 'Автомобилист',
         'home_team': 'Металлург Мг',
         'match_id': '877300',
         'season': season,
         'time': '17:00',
         'overtime': False,
         'penalties': False,
         }
    ]

    assert mock.calls == 1
    assert info == out_info


@pytest.mark.django_db(transaction=True)
@pook.on
def test_parse_finished_match(update_db, get_match_info_finished):
    parser = Parser()
    mock = pook.get(f'https://text.khl.ru/text/877200.html',
                    reply=200,
                    response_body=get_match_info_finished
                    )
    season = KHLSeason.objects.get(id=21)
    match = KHLMatch.objects.create(id=877200, season=season, finished=True)
    info = parser.parse_finished_match(match)

    out_info = {
        'arena': 'МУП «Арена «Мытищи»',
        'city': 'Мытищи',
        'time': '19:30',
        'viewers': '253',
        'match_id': 877200,
        'overtime': False,
        'penalties': False,
        'season': season,
        'finished': True,
    }

    assert mock.calls == 1
    assert info == out_info


@pytest.mark.django_db(transaction=True)
@pook.on
def test_parse_teams(update_db, get_teams_html, get_teams):
    parser = Parser()
    season = KHLSeason.objects.get(id=21)
    mock1 = pook.get('https://www.khl.ru/standings/1097/division/',
                     reply=200,
                     response_body=get_teams_html
                     )
    mock2 = pook.get('https://www.khl.ru/clubs/ska/arena/',
                     reply=200,
                     response_body=get_teams[0]
                     )
    mock3 = pook.get('https://www.khl.ru/clubs/jokerit/arena/',
                     reply=200,
                     response_body=get_teams[1]
                     )
    mock4 = pook.get('https://www.khl.ru/clubs/dynamo_msk/arena/',
                     reply=200,
                     response_body=get_teams[2]
                     )
    mock5 = pook.get('https://www.khl.ru/clubs/cska/arena/',
                     reply=200,
                     response_body=get_teams[3]
                     )
    mock6 = pook.get('https://www.khl.ru/clubs/metallurg_mg/arena/',
                     reply=200,
                     response_body=get_teams[4]
                     )
    mock7 = pook.get('https://www.khl.ru/clubs/traktor/arena/',
                     reply=200,
                     response_body=get_teams[5]
                     )
    mock8 = pook.get('https://www.khl.ru/clubs/salavat_yulaev/arena/',
                     reply=200,
                     response_body=get_teams[6]
                     )
    mock9 = pook.get('https://www.khl.ru/clubs/avangard/arena/',
                     reply=200,
                     response_body=get_teams[7]
                     )

    teams = [
        {'name': 'СКА',
         'img': 'https://www.khl.ru/images/teams/ru/1097/24',
         'city': 'Санкт-Петербург',
         'arena': 'МСРК «Ледовый Дворец»',
         'division': 'Боброва',
         'conference': 'Запад',
         'season': season},
        {'name': 'Йокерит',
         'img': 'https://www.khl.ru/images/teams/ru/1097/450',
         'city': 'Хельсинки',
         'arena': '«Хартвалл Арена»',
         'division': 'Боброва',
         'conference': 'Запад',
         'season': season},
        {'name': 'Динамо М',
         'img': 'https://www.khl.ru/images/teams/ru/1097/719',
         'city': 'Москва',
         'arena': '«ВТБ Арена»',
         'division': 'Тарасова',
         'conference': 'Запад',
         'season': season},
        {'name': 'ЦСКА',
         'img': 'https://www.khl.ru/images/teams/ru/1097/2',
         'city': 'Москва',
         'arena': 'МСК «ЦСКА Арена»',
         'division': 'Тарасова',
         'conference': 'Запад',
         'season': season},
        {'name': 'Металлург Мг',
         'img': 'https://www.khl.ru/images/teams/ru/1097/37',
         'city': 'Магнитогорск',
         'arena': 'УКРК «Арена Металлург»',
         'division': 'Харламова',
         'conference': 'Восток',
         'season': season},
        {'name': 'Трактор',
         'img': 'https://www.khl.ru/images/teams/ru/1097/25',
         'city': 'Челябинск',
         'arena': 'ЛА «Трактор» им. В. Белоусова',
         'division': 'Харламова',
         'conference': 'Восток',
         'season': season},
        {'name': 'Салават Юлаев',
         'img': 'https://www.khl.ru/images/teams/ru/1097/38',
         'city': 'Уфа',
         'arena': 'УСА «Уфа-Арена»',
         'division': 'Чернышева',
         'conference': 'Восток',
         'season': season},
        {'name': 'Авангард',
         'img': 'https://www.khl.ru/images/teams/ru/1097/34',
         'city': 'Омск',
         'arena': 'ЛД «Арена «Балашиха» им. Ю. Ляпкина',
         'division': 'Чернышева',
         'conference': 'Восток',
         'season': season}
    ]

    out = parser.parse_teams(season)

    assert mock1.calls == 1
    assert mock2.calls == 1
    assert mock3.calls == 1
    assert mock4.calls == 1
    assert mock5.calls == 1
    assert mock6.calls == 1
    assert mock7.calls == 1
    assert mock8.calls == 1
    assert mock9.calls == 1

    assert out == teams


@pytest.mark.django_db(transaction=True)
@pook.on
def test_parse_protocol(update_db, get_protocol, get_protocol1):
    mock1 = pook.get('https://text.khl.ru/text/872656.html',
                     reply=200,
                     response_body=get_protocol1
                     )
    mock2 = pook.get('https://text.khl.ru/text/877161.html',
                     reply=200,
                     response_body=get_protocol
                     )
    match1 = KHLMatch.objects.create(id=872656, finished=True)
    match2 = KHLMatch.objects.create(id=877161, finished=True)

    out_home = {
        'team': 'Йокерит',
        'blocks': '7',
        'faceoff': '31',
        'faceoff_p': '65.96',
        'fop': '4',
        'g': '6',
        'g_1': 1,
        'g_2': 3,
        'g_3': 2,
        'g_b': 0,
        'g_ot': 0,
        'hits': '7',
        'match_id': 872656,
        'nshv': '00:06:37',
        'pd': '66.65',
        'penalty': '12',
        'sh': 47,
        'sog': '28',
        'time_a': '00:12:21',
        'vvsh': '00:19:42'
    }
    out_guest = {
        'team': 'Динамо М',
        'blocks': '6',
        'faceoff': '16',
        'faceoff_p': '34.04',
        'fop': '4',
        'g': '1',
        'g_1': 0,
        'g_2': 0,
        'g_3': 1,
        'g_b': 0,
        'g_ot': 0,
        'hits': '14',
        'match_id': 872656,
        'nshv': '00:06:37',
        'pd': '67.27',
        'penalty': '12',
        'sh': 52,
        'sog': '30',
        'time_a': '00:09:47',
        'vvsh': '00:17:13'
    }
    parser = Parser()
    row_home, row_guest = parser.parse_protocol(match1)
    assert row_home == out_home
    assert row_guest == out_guest
    assert mock1.calls == 1

    out_home = {
        'team': 'Авангард',
        'blocks': '22',
        'faceoff': '32',
        'faceoff_p': '55.17',
        'fop': '5',
        'g': '4',
        'g_1': 1,
        'g_2': 0,
        'g_3': 3,
        'g_b': 0,
        'g_ot': 0,
        'hits': '16',
        'match_id': 877161,
        'nshv': '00:06:40',
        'pd': '66.31',
        'penalty': '4',
        'sh': 44,
        'sog': '22',
        'time_a': '00:08:41',
        'vvsh': '00:16:38'
    }
    out_guest = {
        'team': 'ЦСКА',
        'blocks': '14',
        'faceoff': '26',
        'faceoff_p': '44.83',
        'fop': '1',
        'g': 0,
        'g_1': 0,
        'g_2': 0,
        'g_3': 0,
        'g_b': 0,
        'g_ot': 0,
        'hits': '14',
        'match_id': 877161,
        'nshv': '00:06:40',
        'pd': '68.97',
        'penalty': '12',
        'sh': 66,
        'sog': '30',
        'time_a': '00:10:37',
        'vvsh': '00:19:11'
    }
    row_home, row_guest = parser.parse_protocol(match2)
    assert row_home == out_home
    assert row_guest == out_guest
    assert mock2.calls == 1


def test_row_update_type():
    parser = Parser()
    row = {
        'sh': '66',
        'sog': '',
        'time_a': '10:37',
        'vvsh': ''
    }
    out_row = {'sh': '66', 'sog': 0, 'time_a': '00:10:37', 'vvsh': '00:00:00'}
    new_row = parser._row_update_type(row)
    assert new_row == out_row

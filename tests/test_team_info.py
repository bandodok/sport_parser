import pytest
import pook

from sport_parser.khl.parsers.team_info import parse_teams_in_season


@pytest.fixture()
def get_teams_html():
    return open('tests/fixtures/teams.html', encoding='utf-8').read()


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


@pook.on
def test_parse_teams_in_season(get_teams_html, get_teams):
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
     ['СКА',
      'https://www.khl.ru/images/teams/ru/1097/24',
      'Санкт-Петербург',
      'МСРК «Ледовый Дворец»',
      'Боброва',
      'Запад',
      '21'],
     ['Йокерит',
      'https://www.khl.ru/images/teams/ru/1097/450',
      'Хельсинки',
      '«Хартвалл Арена»',
      'Боброва',
      'Запад',
      '21'],
     ['Динамо М',
      'https://www.khl.ru/images/teams/ru/1097/719',
      'Москва',
      '«ВТБ Арена»',
      'Тарасова',
      'Запад',
      '21'],
     ['ЦСКА',
      'https://www.khl.ru/images/teams/ru/1097/2',
      'Москва',
      'МСК «ЦСКА Арена»',
      'Тарасова',
      'Запад',
      '21'],
     ['Металлург Мг',
      'https://www.khl.ru/images/teams/ru/1097/37',
      'Магнитогорск',
      'УКРК «Арена Металлург»',
      'Харламова',
      'Восток',
      '21'],
     ['Трактор',
      'https://www.khl.ru/images/teams/ru/1097/25',
      'Челябинск',
      'ЛА «Трактор» им. В. Белоусова',
      'Харламова',
      'Восток',
      '21'],
     ['Салават Юлаев',
      'https://www.khl.ru/images/teams/ru/1097/38',
      'Уфа',
      'УСА «Уфа-Арена»',
      'Чернышева',
      'Восток',
      '21'],
     ['Авангард',
      'https://www.khl.ru/images/teams/ru/1097/34',
      'Омск',
      'ЛД «Арена «Балашиха» им. Ю. Ляпкина',
      'Чернышева',
      'Восток',
      '21']
    ]

    out = parse_teams_in_season(1097)

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

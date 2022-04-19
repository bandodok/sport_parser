import pook
import pytest
from sport_parser.khl.models import KHLSeason, KHLMatch
from sport_parser.core.updater import Updater
from sport_parser.core.config import Config


@pytest.fixture()
def get_teams():
    teams = []
    with open('tests/fixtures/parse_season/parse_season_teams/jokerit.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/parse_season/parse_season_teams/avtomobilist.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/parse_season/parse_season_teams/metallurg_mg.html', encoding='utf-8') as f:
        teams.append(f.read())
    with open('tests/fixtures/parse_season/parse_season_teams/kunlun.html', encoding='utf-8') as f:
        teams.append(f.read())
    return teams


@pytest.fixture
def get_calendar():
    return open('tests/fixtures/parse_season/calendar.html', encoding='utf-8').read()


@pytest.fixture
def get_html_teams():
    return open('tests/fixtures/parse_season/parse_season_teams.html', encoding='utf-8').read()


@pytest.fixture
def get_protocol():
    return open('tests/fixtures/parse_season/protocol877200.html', encoding='utf-8').read()


@pytest.mark.django_db(transaction=True)
@pook.on
def test_parse_season(get_teams, get_html_teams, get_calendar, get_protocol):
    KHLSeason.objects.create(id=21, external_id=1097)
    mock = pook.get('https://www.khl.ru/standings/1097/division/',
                    reply=200,
                    response_body=get_html_teams
                    )
    mock1 = pook.get('https://www.khl.ru/clubs/jokerit/arena/',
                     reply=200,
                     response_body=get_teams[0]
                     )
    mock2 = pook.get('https://www.khl.ru/clubs/avtomobilist/arena/',
                     reply=200,
                     response_body=get_teams[1]
                     )
    mock3 = pook.get('https://www.khl.ru/clubs/metallurg_mg/arena/',
                     reply=200,
                     response_body=get_teams[2]
                     )
    mock4 = pook.get('https://www.khl.ru/clubs/kunlun/arena/',
                     reply=200,
                     response_body=get_teams[3]
                     )
    mock_calendar = pook.get('https://www.khl.ru/calendar/1097/00/',
                             reply=200,
                             response_body=get_calendar
                             )
    mock_protocol = pook.get('https://text.khl.ru:443/text/877200.html',
                             reply=200,
                             response_body=get_protocol
                             )
    mock_protocol1 = pook.get('https://text.khl.ru:443/text/877200.html',
                              reply=200,
                              response_body=get_protocol
                              )
    updater = Updater(config=Config)
    updater.parse_season(21)

    assert mock.calls == 1
    assert mock1.calls == 1
    assert mock2.calls == 1
    assert mock3.calls == 1
    assert mock4.calls == 1
    assert mock_calendar.calls == 1
    assert mock_protocol.calls == 1
    assert mock_protocol1.calls == 1

    assert KHLMatch.objects.get(id=877200)
    assert KHLMatch.objects.get(id=877300)

    match1 = KHLMatch.objects.get(id=877200)
    match2 = KHLMatch.objects.get(id=877300)

    match1_teams = [team.name for team in match1.teams.all()]
    match2_teams = [team.name for team in match2.teams.all()]

    assert 'Куньлунь РС' in match1_teams
    assert 'Йокерит' in match1_teams
    assert 'Металлург Мг' in match2_teams
    assert 'Автомобилист' in match2_teams

    assert match1.finished is True
    assert match2.finished is False

    match1_protocols = [protocol.team.name for protocol in match1.protocols.all()]

    assert 'Куньлунь РС' in match1_protocols
    assert 'Йокерит' in match1_protocols

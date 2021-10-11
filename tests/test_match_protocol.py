import pytest
import pook

from sport_parser.khl.parsers.match_protocol import row_update_type, get_khl_protocol


@pytest.fixture
def get_protocol():
    return open('tests/fixtures/protocol.html', encoding='utf-8').read()


@pytest.fixture
def get_protocol1():
    return open('tests/fixtures/protocol1.html', encoding='utf-8').read()


@pook.on
def test_get_khl_protocol(get_protocol, get_protocol1):
    mock1 = pook.get('https://text.khl.ru/text/872656.html',
                     reply=200,
                     response_body=get_protocol1
                     )
    mock2 = pook.get('https://text.khl.ru/text/877161.html',
                     reply=200,
                     response_body=get_protocol
                     )
    out_home = {
        'team': 'Йокерит',
        'blocks': '7',
        'faceoff': '31',
        'faceoff_p': '65.96',
        'fop': '4',
        'g': '6',
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
    row_home, row_guest = get_khl_protocol(872656)
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
        'hits': '16',
        'match_id': 877161,
        'nshv': '00:06:40',
        'pd': '66.31',
        'penalty': '4',
        'sh': '44',
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
        'hits': '14',
        'match_id': 877161,
        'nshv': '00:06:40',
        'pd': '68.97',
        'penalty': '12',
        'sh': '66',
        'sog': '30',
        'time_a': '00:10:37',
        'vvsh': '00:19:11'
    }
    row_home, row_guest = get_khl_protocol(877161)
    assert row_home == out_home
    assert row_guest == out_guest
    assert mock2.calls == 1


def test_row_update_type():
    row = {
        'sh': '66',
        'sog': '',
        'time_a': '10:37',
        'vvsh': ''
    }
    out_row = {'sh': '66', 'sog': 0, 'time_a': '00:10:37', 'vvsh': '00:00:00'}
    new_row = row_update_type(row)
    assert new_row == out_row

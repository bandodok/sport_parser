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
    out_home = ['Йокерит', 872656, '6', '28', '12', '31', '65.96', '7', '7', '4', '00:12:21', '00:19:42', '00:06:37',
                '66.65', '47']
    out_guest = ['Динамо М', 872656, '1', '30', '12', '16', '34.04', '6', '14', '4', '00:09:47', '00:17:13', '00:06:37',
                 '67.27', '52']
    row_home, row_guest = get_khl_protocol(872656)
    assert row_home == out_home
    assert row_guest == out_guest
    assert mock1.calls == 1

    out_home = ['Авангард', 877161, '4', '22', '4', '32', '55.17', '22', '16', '5', '00:08:41', '00:16:38', '00:06:40',
                '66.31', '44']
    out_guest = ['ЦСКА', 877161, 0, '30', '12', '26', '44.83', '14', '14', '1', '00:10:37', '00:19:11', '00:06:40',
                 '68.97', '66']
    row_home, row_guest = get_khl_protocol(877161)
    assert row_home == out_home
    assert row_guest == out_guest
    assert mock2.calls == 1


def test_row_update_type():
    row = [1, '2', '', '14:33']
    out_row = [1, '2', 0, '00:14:33', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    new_row = row_update_type(row)
    assert new_row == out_row

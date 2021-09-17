import pytest
import pook

from sport_parser.khl.parsers.match_info import get_khl_match_info, month_to_int_replace


@pytest.fixture
def get_protocol():
    return open('tests/fixtures/protocol.html', encoding='utf-8').read()


def test_month_to_int_replace():
    assert month_to_int_replace('янв.') == '01'
    assert month_to_int_replace('марта') == '03'
    assert month_to_int_replace('дек.') == '12'


@pook.on
def test_get_khl_match_info(get_protocol):
    url = 'https://text.khl.ru/text/877160.html'
    mock = pook.get(url,
                    reply=200,
                    response_body=get_protocol
                    )
    info = get_khl_match_info(877160)
    out_info = [877160, '2021-09-01 19:00', '21', 'ЛД «Арена «Балашиха» им. Ю. Ляпкина', 'Балашиха', '981']
    assert mock.calls == 1
    assert info == out_info

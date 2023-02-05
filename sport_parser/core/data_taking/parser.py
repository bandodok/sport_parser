import json
from abc import abstractmethod
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Collection, Callable, Coroutine, TypeVar, Any
import asyncio

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from selenium import webdriver

from sport_parser.core.models import SeasonModel


_T = TypeVar('_T')


class ParseMethods(Enum):
    SYNC = 'SYNC'
    ASYNC = 'ASYNC'


class MatchStatus(Enum):
    SCHEDULED = 'scheduled'
    FINISHED = 'finished'
    POSTPONED = 'postponed'
    LIVE = 'live'
    GAME_OVER = 'game over'


@dataclass
class TeamData:
    name: str
    season_num: int
    img: str
    city: str
    arena: str
    division: str
    conference:  str


@dataclass
class MatchData:
    id: int
    season_num: int
    date: datetime
    status: MatchStatus
    home_team_name: str
    guest_team_name: str
    penalties: bool = False
    overtime: bool = False
    arena: str = ''
    city: str = ''
    viewers: int = 0


@dataclass
class ProtocolRequiredStats:
    g: int
    g_1: int
    g_2: int
    g_3: int
    g_ot: int
    g_b: int


@dataclass
class ProtocolData:
    team_name: str
    required_stats: ProtocolRequiredStats
    additional_stats: dict


class MatchProtocolsData(NamedTuple):
    match_id: int
    home_protocol: ProtocolData
    guest_protocol: ProtocolData


@dataclass
class MatchLiveProtocolsData:
    home_protocol: dict
    guest_protocol: dict


@dataclass
class MatchLiveData:
    match_id: int
    status: str
    team1_score: int
    team2_score: int
    protocols: MatchLiveProtocolsData


class Parser:

    parser_type: ParseMethods

    def __init__(self, parse_method):
        self.parser_type = parse_method

    @abstractmethod
    def parse_teams(self, season: SeasonModel) -> list[TeamData]:
        """
        Парсит информацию о командах сезона

        :param season: строка сезона модели SeasonModel
        :return: список информации по командам в формате TeamData
        """
        pass

    @abstractmethod
    def parse_calendar(self, season: SeasonModel) -> list[MatchData]:
        """
        Парсит основную информацию о матчах сезона.

        :param season: строка сезона модели SeasonModel
        :return: список информации по матчам сезона в формате MatchData
        """
        pass

    @abstractmethod
    def parse_matches_additional_info(self, matches: list[MatchData]) -> None:
        """
        Парсит дополнительную информацию по матчам и дополняет MatchData.
        Вызывается после парсинга календаря для получения информации, которую не удалось получить.

        :param matches: список с информацией о матчах в формате MatchData
        """
        pass

    @abstractmethod
    def is_match_finished(self, match_id: int) -> bool:
        """
        Проверяет по id завершен ли матч.
        Вызывается во время проверки последних матчей на завершение.

        :param match_id: id матча
        :return: True, если матч завершен
        """
        pass

    @abstractmethod
    def parse_finished_match(self, match: MatchData) -> MatchData:
        """
        Парсит информацию по завершенному матчу.
        Вызывается для обновления информации после завершения матча.

        :param match: информация о матче в формате MatchData
        :return: обновленная информация о матче в формате MatchData
        """
        pass

    @abstractmethod
    def parse_protocol(self, match_id: int) -> MatchProtocolsData:
        """
        Возвращает протокол матча для обеих команд.

        :param match_id: id матча
        :return: протокол матча в формате MatchProtocolsData
        """
        pass

    @abstractmethod
    def parse_live_match(self, match_id: int) -> MatchLiveData:
        """
        Возвращает данные текущего матча для обеих команд.

        :param match_id: id матча
        :return: данные матча в формате MatchLiveData
        """
        pass

    @staticmethod
    def get_request_content(url) -> BeautifulSoup:
        r = requests.get(url)
        return BeautifulSoup(r.content, 'html.parser')

    @staticmethod
    def get_api_request_content(url) -> dict:
        r = requests.get(url).content
        return json.loads(r)

    @staticmethod
    async def get_async_api_response(url) -> dict:
        async with aiohttp.request('GET', url) as response:
            content = await response.read()
            return json.loads(content)

    async def get_async_response(self, url) -> BeautifulSoup:
        if self.parser_type == ParseMethods.ASYNC:
            connector = aiohttp.TCPConnector(limit=50)
            async with aiohttp.ClientSession(connector=connector) as sess:
                async with sess.request('GET', url) as response:
                    content = await response.read()
        else:
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('https://', adapter)
            r = session.get(url, timeout=5)
            content = r.content
        return BeautifulSoup(content, 'html.parser')

    @staticmethod
    def get_selenium_content(url) -> BeautifulSoup:
        loc = os.getenv('CHROMEDRIVER')
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument('ignore-certificate-errors')
        capabilities = webdriver.DesiredCapabilities().CHROME
        capabilities['acceptSslCerts'] = True
        driver = webdriver.Chrome(loc, options=op)
        driver.get(url)
        r = driver.page_source
        driver.close()
        return BeautifulSoup(r, 'html.parser')

    def _parse(self, func: Callable[..., Coroutine[Any, Any, _T]], iterable: Collection, *args, **kwargs) -> list[_T]:
        if self.parser_type == ParseMethods.ASYNC:
            loop = asyncio.new_event_loop()
            tasks = [asyncio.ensure_future(func(item, *args, **kwargs), loop=loop) for item in iterable]
            awaited = asyncio.wait(tasks)
            results = loop.run_until_complete(awaited)[0]
            return [task.result() for task in results]
        else:
            return [asyncio.run(func(item, *args, **kwargs)) for item in iterable]

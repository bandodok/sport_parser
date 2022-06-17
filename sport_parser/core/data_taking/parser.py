import json
from abc import abstractmethod
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NamedTuple

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from sport_parser.core.models import SeasonModel

from sport_parser.core.data_analysis.formatter import Formatter


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
        Парсит основную информацию о матчах сезона

        :param season: строка сезона модели SeasonModel
        :return: список информации по матчам сезона в формате MatchData
        """
        pass

    @abstractmethod
    def parse_match_additional_info(self, match: MatchData) -> None:
        """
        Парсит дополнительную информацию по конкретному матчу и дополняет MatchData.
        Вызывается после парсинга календаря для получения информации, которую не удалось получить.

        :param match: информация о матче в формате MatchData
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

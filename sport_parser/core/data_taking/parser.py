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


class Parser:
    def __init__(self, config):
        self.formatter = Formatter(config)

    @abstractmethod
    def parse_teams(self, season):
        pass

    @abstractmethod
    def parse_calendar(self, season, *, webdriver=None):
        """Загружает базовую информацию по матчам в базу данных"""
        pass

    @abstractmethod
    def parse_match(self, match):
        pass

    @abstractmethod
    def parse_protocol(self, match):
        """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
        pass

    @abstractmethod
    def parse_live_protocol(self, match):
        """Возвращает статус и протокол текущего матча для параметров, обновляемых в течение матча"""
        pass

    @staticmethod
    def get_request_content(url):
        r = requests.get(url)
        return BeautifulSoup(r.content, 'html.parser')

    @staticmethod
    def get_api_request_content(url):
        r = requests.get(url).content
        return json.loads(r)

    @staticmethod
    def get_selenium_content(url):
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

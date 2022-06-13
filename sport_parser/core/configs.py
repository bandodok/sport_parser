from enum import Enum

from sport_parser.khl.config import KHLConfig
from sport_parser.nhl.config import NHLConfig


class ConfigType(Enum):
    khl = KHLConfig
    nhl = NHLConfig

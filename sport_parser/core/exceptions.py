class SportParserException(Exception):
    """Базовый класс исключений приложения"""
    pass


class UnableToGetProtocolException(SportParserException):
    """Вызывается при невозможности получить протокол матча"""
    pass


class UnableToCalculateBarStats(SportParserException):
    """Вызывается при попытке рассчитать статистику для полосок для незавершенного матча"""
    pass


class SeasonDoesNotExist(SportParserException):
    """Вызывается при попытке получить класс несуществующего сезона"""
    pass


class TeamDoesNotExist(SportParserException):
    """Вызывается при попытке получить класс несуществующей команды"""
    pass


class MatchDoesNotExist(SportParserException):
    """Вызывается при попытке получить класс несуществующего матча"""
    pass

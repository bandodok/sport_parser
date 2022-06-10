class SportParserException(Exception):
    """Базовый класс исключений приложения"""
    pass


class UnableToGetProtocolException(SportParserException):
    """Вызывается при невозможности получить протокол матча"""
    pass


class UnableToCalculateBarStats(SportParserException):
    """Вызывается при попытке рассчитать статистику для полосок для незавершенного матча"""
    pass

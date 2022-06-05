class SportParserException(Exception):
    """Базовый класс исключений приложения"""
    pass


class UnableToGetProtocolException(SportParserException):
    """Вызывается при невозможности получить протокол матча"""
    pass

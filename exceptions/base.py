"""
Базовые исключения для библиотеки
"""


class Anime365Error(Exception):
    """Базовое исключение для всех ошибок библиотеки"""
    pass


class ValidationError(Anime365Error):
    """Ошибка валидации входных данных"""
    pass


class NetworkError(Anime365Error):
    """Ошибка сети"""
    pass

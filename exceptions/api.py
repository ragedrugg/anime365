"""
Исключения для API
"""

from .base import Anime365Error


class APIError(Anime365Error):
    """Ошибка API"""
    pass


class NotFoundError(APIError):
    """Ресурс не найден (404)"""
    pass


class RateLimitError(APIError):
    """Превышен лимит запросов (429)"""
    pass


class ServerError(APIError):
    """Ошибка сервера (5xx)"""
    pass


class ClientError(APIError):
    """Ошибка клиента (4xx)"""
    pass

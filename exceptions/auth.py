"""
Исключения для авторизации
"""

from .base import Anime365Error


class AuthenticationError(Anime365Error):
    """Ошибка авторизации"""
    pass


class TokenError(AuthenticationError):
    """Ошибка с токеном"""
    pass


class LoginError(AuthenticationError):
    """Ошибка входа в систему"""
    pass

"""
Основной клиент anime365
"""

from typing import Optional
from aiohttp import ClientSession

from .base import BaseClient
from .auth import AuthMixin
from .anime import AnimeMixin
from .episodes import EpisodesMixin
from .translations import TranslationsMixin
from .embed import EmbedMixin


class Anime365Client(
    AuthMixin,
    AnimeMixin,
    EpisodesMixin,
    TranslationsMixin,
    EmbedMixin,
    BaseClient
):
    """
    Асинхронный клиент для работы с API anime365 (smotret-anime.online)
    
    Объединяет все возможности библиотеки в одном классе.
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        session: Optional[ClientSession] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Инициализация клиента
        
        Args:
            access_token: Токен доступа (если есть)
            email: Email для авторизации
            password: Пароль для авторизации
            timeout: Таймаут запросов в секундах
            session: Существующая сессия aiohttp (опционально)
            max_retries: Максимальное количество повторных попыток
            retry_delay: Задержка между повторными попытками в секундах
        """
        # Валидация токена при инициализации
        if access_token is not None:
            from ..utils import validate_token
            try:
                validate_token(access_token)
            except ValueError as e:
                from ..exceptions import TokenError
                raise TokenError(str(e))
        
        super().__init__(
            access_token=access_token,
            timeout=timeout,
            session=session,
            max_retries=max_retries,
            retry_delay=retry_delay,
            email=email,
            password=password
        )

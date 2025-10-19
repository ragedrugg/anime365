"""
Базовый клиент для anime365
"""

import logging
from typing import Optional, Dict, Any
from aiohttp import ClientSession, ClientTimeout

from ..exceptions.base import NetworkError
from ..exceptions.auth import AuthenticationError
from ..exceptions.api import APIError, NotFoundError, RateLimitError, ServerError
from ..utils import (
    calculate_retry_delay, sleep_with_jitter, 
    format_error_message, extract_api_error
)


class BaseClient:
    """Базовый класс клиента"""
    
    BASE_URL = "https://smotret-anime.online/api"
    USER_AGENT = "anime365-wrapper-python/1.0.0"
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        timeout: int = 30,
        session: Optional[ClientSession] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Инициализация базового клиента
        
        Args:
            access_token: Токен доступа
            timeout: Таймаут запросов в секундах
            session: Существующая сессия aiohttp
            max_retries: Максимальное количество повторных попыток
            retry_delay: Задержка между повторными попытками в секундах
        """
        self.access_token = access_token
        self.timeout = ClientTimeout(total=timeout)
        self._session = session
        self._own_session = session is None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
    
    async def _ensure_session(self):
        """Обеспечить наличие сессии"""
        if self._session is None:
            self._session = ClientSession(
                timeout=self.timeout,
                headers={"User-Agent": self.USER_AGENT}
            )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        require_auth: bool = False,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос к API с retry механизмом
        
        Args:
            method: HTTP метод (GET, POST)
            endpoint: Endpoint API
            params: Параметры запроса
            require_auth: Требуется ли авторизация
            retry_count: Текущее количество попыток
            
        Returns:
            JSON ответ от API
            
        Raises:
            Anime365Error: Ошибка API
            AuthenticationError: Ошибка авторизации
        """
        await self._ensure_session()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        # Добавляем токен если требуется авторизация
        if require_auth and self.access_token:
            if params is None:
                params = {}
            params["access_token"] = self.access_token
            
        # Выполняем запрос с retry механизмом
        try:
            async with self._session.request(
                method=method,
                url=url,
                params=params
            ) as response:
                # Обработка различных статус кодов
                if response.status == 401:
                    raise AuthenticationError("Неверный токен авторизации")
                elif response.status == 403:
                    raise AuthenticationError("Доступ запрещен")
                elif response.status == 404:
                    raise NotFoundError("Ресурс не найден")
                elif response.status == 414:
                    raise APIError("Запрос слишком длинный")
                elif response.status == 429:
                    # Rate limit - пробуем повторить
                    if retry_count < self.max_retries:
                        delay = calculate_retry_delay(retry_count, self.retry_delay)
                        self.logger.warning(f"Rate limit hit, retrying in {delay:.2f}s (attempt {retry_count + 1})")
                        await sleep_with_jitter(delay)
                        return await self._make_request(method, endpoint, params, require_auth, retry_count + 1)
                    else:
                        raise RateLimitError("Превышен лимит запросов")
                elif response.status >= 500:
                    # Серверные ошибки - пробуем повторить
                    if retry_count < self.max_retries:
                        delay = calculate_retry_delay(retry_count, self.retry_delay)
                        self.logger.warning(f"Server error {response.status}, retrying in {delay:.2f}s (attempt {retry_count + 1})")
                        await sleep_with_jitter(delay)
                        return await self._make_request(method, endpoint, params, require_auth, retry_count + 1)
                    else:
                        error_text = await response.text()
                        raise ServerError(f"HTTP {response.status}: {error_text}")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise APIError(format_error_message(response.status, error_text))
                    
                response_data = await response.json()
                
                # Проверяем на наличие ошибок в ответе
                api_error = extract_api_error(response_data)
                if api_error:
                    raise APIError(api_error)
                
                return response_data
                
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, NotFoundError, RateLimitError, ServerError)):
                raise
            # Сетевые ошибки - пробуем повторить
            if retry_count < self.max_retries:
                delay = calculate_retry_delay(retry_count, self.retry_delay)
                self.logger.warning(f"Network error: {e}, retrying in {delay:.2f}s (attempt {retry_count + 1})")
                await sleep_with_jitter(delay)
                return await self._make_request(method, endpoint, params, require_auth, retry_count + 1)
            else:
                raise NetworkError(f"Ошибка сети: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self._own_session:
            await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._own_session and self._session:
            await self._session.close()
    
    async def close(self):
        """Закрыть сессию"""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

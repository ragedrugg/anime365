"""
Anime365 API Wrapper

Асинхронная библиотека для работы с API anime365 (smotret-anime)
"""

__version__ = "1.0.0"
__author__ = "ragedrugg"

# Основной клиент
from .client import Anime365Client

# Исключения
from .exceptions import (
    Anime365Error,
    AuthenticationError, 
    APIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    NetworkError,
    ValidationError,
    TokenError,
    LoginError,
    ParameterError,
    IDError,
    LimitError,
    QueryError
)

# Константы
from .constants import (
    ANIME_TYPES, EPISODE_TYPES, TRANSLATION_TYPES,
    QUALITY_TYPES, LANGUAGE_TYPES, CONTENT_TYPES,
    FEED_TYPES, ACTIVE_STATUS, PREMIUM_STATUS
)

__all__ = [
    # Основной клиент
    "Anime365Client",
    
    # Исключения
    "Anime365Error",
    "AuthenticationError",
    "APIError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "ValidationError",
    "TokenError",
    "LoginError",
    "ParameterError",
    "IDError",
    "LimitError",
    "QueryError",
    
    # Модели данных
    "Series",
    "Episode", 
    "Translation",
    "User",
    "EmbedData",
    "Title",
    "Link",
    "Description",
    "Genre",
    "DownloadOption",
    "StreamOption",
    
    # Константы
    "ANIME_TYPES",
    "EPISODE_TYPES", 
    "TRANSLATION_TYPES",
    "QUALITY_TYPES",
    "LANGUAGE_TYPES",
    "CONTENT_TYPES",
    "FEED_TYPES",
    "ACTIVE_STATUS",
    "PREMIUM_STATUS"
]
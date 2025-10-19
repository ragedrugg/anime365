"""
Инициализация моделей
"""

from .common import Title, Link, Description, Genre, User
from .anime import Series, SeriesResponse
from .episodes import Episode, EpisodeResponse
from .translations import (
    Translation, TranslationResponse, TranslationsResponse,
    DownloadOption, StreamOption, EmbedData, EmbedResponse,
    UserResponse, LoginResponse
)

# Пересборка моделей для решения циклических ссылок
SeriesResponse.model_rebuild()
EpisodeResponse.model_rebuild()
TranslationResponse.model_rebuild()
TranslationsResponse.model_rebuild()
EmbedResponse.model_rebuild()
UserResponse.model_rebuild()

__all__ = [
    # Common models
    "Title", "Link", "Description", "Genre", "User",
    
    # Anime models
    "Series", "SeriesResponse",
    
    # Episode models
    "Episode", "EpisodeResponse",
    
    # Translation models
    "Translation", "TranslationResponse", "TranslationsResponse",
    "DownloadOption", "StreamOption", "EmbedData", "EmbedResponse",
    "UserResponse", "LoginResponse",
]

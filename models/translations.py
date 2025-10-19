"""
Модели для переводов
"""

from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from .episodes import Episode
    from .anime import Series
    from .common import User


class Translation(BaseModel):
    """Модель перевода аниме"""
    id: int
    addedDateTime: Optional[datetime] = None      # Дата добавления
    activeDateTime: Optional[datetime] = None     # Дата активации
    authorsList: Optional[List[str]] = Field(default_factory=list)  # Список авторов
    fansubsTranslationId: Optional[int] = None     # ID в базе фансабов
    isActive: Optional[int] = None                 # Активен ли перевод
    priority: Optional[int] = None                 # Приоритет
    qualityType: Optional[str] = None              # Тип качества
    type: Optional[str] = None                    # Тип перевода
    typeKind: Optional[str] = None                 # Вид перевода
    typeLang: Optional[str] = None                 # Язык перевода
    updatedDateTime: Optional[datetime] = None      # Дата обновления
    title: Optional[str] = None                    # Название перевода
    seriesId: Optional[int] = None                 # ID аниме
    episodeId: Optional[int] = None               # ID эпизода
    url: Optional[str] = None                     # URL страницы перевода
    embedUrl: Optional[str] = None                 # URL для embed
    authorsSummary: Optional[str] = None           # Краткое описание авторов
    duration: Optional[float] = None                 # Длительность в секундах
    width: Optional[int] = None                    # Ширина видео
    height: Optional[int] = None                   # Высота видео
    episode: Optional['Episode'] = None            # Информация об эпизоде
    series: Optional['Series'] = None              # Информация об аниме


class TranslationResponse(BaseModel):
    """Ответ с информацией о переводе"""
    data: Translation


class TranslationsResponse(BaseModel):
    """Ответ со списком переводов"""
    data: List[Translation]


class DownloadOption(BaseModel):
    """Опция для скачивания"""
    height: int
    url: Optional[str] = None


class StreamOption(BaseModel):
    """Опция для стриминга"""
    height: int
    urls: List[str] = Field(default_factory=list)


class EmbedData(BaseModel):
    """Данные для embed плеера"""
    embedUrl: Optional[str] = None
    download: List[DownloadOption] = Field(default_factory=list)
    stream: List[StreamOption] = Field(default_factory=list)
    subtitlesUrl: Optional[str] = None
    subtitlesVttUrl: Optional[str] = None


class EmbedResponse(BaseModel):
    """Ответ с embed данными"""
    data: EmbedData


class UserResponse(BaseModel):
    """Ответ с информацией о пользователе"""
    data: 'User'


class LoginResponse(BaseModel):
    """Ответ авторизации"""
    access_token: str

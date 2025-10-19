"""
Модели для эпизодов
"""

from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from .anime import Series
    from .translations import Translation


class Episode(BaseModel):
    """Модель эпизода аниме"""
    id: int
    episodeFull: Optional[str] = None  # Полное название эпизода
    episodeInt: Optional[str] = None   # Номер эпизода (строка)
    episodeTitle: Optional[str] = None  # Название эпизода
    episodeType: Optional[str] = None   # Тип эпизода
    firstUploadedDateTime: Optional[datetime] = None  # Дата первой загрузки
    isActive: Optional[int] = None      # Активен ли эпизод
    isFirstUploaded: Optional[int] = None  # Первая загрузка
    seriesId: Optional[int] = None      # ID аниме
    translations: Optional[List['Translation']] = Field(default_factory=list)  # Список переводов
    series: Optional['Series'] = None   # Информация об аниме


class EpisodeResponse(BaseModel):
    """Ответ с информацией об эпизоде"""
    data: Episode

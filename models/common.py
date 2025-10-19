"""
Общие модели данных
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Title(BaseModel):
    """Названия аниме на разных языках"""
    ru: Optional[str] = None
    romaji: Optional[str] = None
    ja: Optional[str] = None
    en: Optional[str] = None


class Link(BaseModel):
    """Ссылка на внешний ресурс"""
    title: str
    url: Optional[str] = None  # Может быть относительным URL
    
    @classmethod
    def validate_url(cls, v):
        """Валидация URL - принимает как абсолютные, так и относительные URL"""
        if v is None:
            return None
        if isinstance(v, str):
            # Если это относительный URL, оставляем как есть
            if not v.startswith(('http://', 'https://')):
                return v
            # Если это абсолютный URL, валидируем
            try:
                from pydantic import HttpUrl
                return str(HttpUrl(v))
            except:
                return v
        return v


class Description(BaseModel):
    """Описание аниме из источника"""
    source: str
    value: str
    updatedDateTime: datetime


class Genre(BaseModel):
    """Жанр аниме"""
    id: int
    title: str
    url: Optional[str] = None  # Может быть относительным URL


class User(BaseModel):
    """Модель пользователя"""
    isLogined: bool
    id: Optional[int] = None              # ID пользователя
    name: Optional[str] = None            # Имя пользователя
    isPremium: Optional[bool] = None      # Премиум ли пользователь
    premiumUntil: Optional[str] = None    # До какого числа действует премиум

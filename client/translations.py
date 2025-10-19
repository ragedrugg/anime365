"""
Модуль для работы с переводами
"""

from typing import List, Optional
from .base import BaseClient
from ..exceptions.validation import IDError, LimitError, ParameterError
from ..utils import validate_id, validate_limit, validate_offset, validate_feed, build_params
from ..models import (
    Translation, TranslationResponse, TranslationsResponse
)


class TranslationsMixin(BaseClient):
    """Миксин для работы с переводами"""
    
    async def get_translations(
        self,
        feed: str = "recent",
        limit: int = 20,
        offset: int = 0,
        afterId: Optional[int] = None,
        series_id: Optional[int] = None,
        fields: Optional[List[str]] = None
    ) -> List[Translation]:
        """
        Получить список переводов
        
        Args:
            feed: Тип ленты (recent, id, all)
            limit: Количество элементов
            offset: Смещение
            afterId: Получить переводы после указанного ID
            series_id: Фильтр по ID аниме
            fields: Список полей для получения
            
        Returns:
            Список переводов
        """
        # Валидация параметров
        try:
            feed = validate_feed(feed)
            limit = validate_limit(limit)
            offset = validate_offset(offset)
            if afterId:
                afterId = validate_id(afterId, "afterId")
            if series_id:
                series_id = validate_id(series_id, "series_id")
        except ValueError as e:
            raise ParameterError(str(e))
        
        params = build_params(
            feed=feed,
            limit=limit,
            offset=offset,
            afterId=afterId,
            series_id=series_id,
            fields=fields
        )
        
        response = await self._make_request("GET", "/translations/", params)
        return TranslationsResponse(**response).data
        
    async def get_translation(self, translation_id: int) -> Translation:
        """
        Получить информацию о конкретном переводе
        
        Args:
            translation_id: ID перевода
            
        Returns:
            Информация о переводе
        """
        try:
            translation_id = validate_id(translation_id, "translation_id")
        except ValueError as e:
            raise IDError(str(e))
            
        response = await self._make_request("GET", f"/translations/{translation_id}")
        return TranslationResponse(**response).data
    
    async def get_recent_translations(self, limit: int = 20) -> List[Translation]:
        """
        Получить последние переводы онгоингов
        
        Args:
            limit: Количество переводов
            
        Returns:
            Список последних переводов
        """
        try:
            limit = validate_limit(limit)
        except ValueError as e:
            raise LimitError(str(e))
            
        return await self.get_translations(feed="recent", limit=limit)
    
    async def get_all_translations_after(self, after_id: int, limit: int = 1000) -> List[Translation]:
        """
        Получить все переводы после указанного ID (для полного сканирования)
        
        Args:
            after_id: ID после которого получать переводы
            limit: Количество переводов за запрос
            
        Returns:
            Список переводов
        """
        try:
            after_id = validate_id(after_id, "after_id")
            limit = validate_limit(limit)
        except ValueError as e:
            raise ParameterError(str(e))
            
        return await self.get_translations(feed="id", afterId=after_id, limit=limit)
    
    async def get_anime_translations(self, series_id: int, limit: int = 1000) -> List[Translation]:
        """
        Получить все переводы конкретного аниме
        
        Args:
            series_id: ID аниме
            limit: Количество переводов
            
        Returns:
            Список переводов аниме
        """
        try:
            series_id = validate_id(series_id, "series_id")
            limit = validate_limit(limit)
        except ValueError as e:
            raise ParameterError(str(e))
            
        return await self.get_translations(series_id=series_id, limit=limit)

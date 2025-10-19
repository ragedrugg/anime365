"""
Модуль для работы с аниме
"""

from typing import List, Optional
from .base import BaseClient
from ..exceptions.validation import IDError, QueryError
from ..utils import validate_id, validate_limit, validate_offset, validate_query, build_params
from ..models import Series, SeriesResponse


class AnimeMixin(BaseClient):
    """Миксин для работы с аниме"""
    
    async def get_series(
        self,
        limit: int = 20,
        offset: int = 0,
        fields: Optional[List[str]] = None,
        query: Optional[str] = None,
        myAnimeListId: Optional[int] = None,
        chips: Optional[str] = None,
        pretty: bool = False
    ) -> List[Series]:
        """
        Получить список аниме
        
        Args:
            limit: Количество элементов на странице
            offset: Смещение от начала
            fields: Список полей для получения
            query: Поиск по названию
            myAnimeListId: Фильтр по ID на MyAnimeList
            chips: Расширенный фильтр
            pretty: Читабельный формат JSON
            
        Returns:
            Список аниме
        """
        # Валидация параметров
        try:
            limit = validate_limit(limit)
            offset = validate_offset(offset)
            if query:
                query = validate_query(query)
            if myAnimeListId:
                myAnimeListId = validate_id(myAnimeListId, "myAnimeListId")
        except ValueError as e:
            raise QueryError(str(e))
        
        params = build_params(
            limit=limit,
            offset=offset,
            fields=fields,
            query=query,
            myAnimeListId=myAnimeListId,
            chips=chips,
            pretty="1" if pretty else None
        )
        
        response = await self._make_request("GET", "/series/", params)
        data = SeriesResponse(**response).data
        return data if isinstance(data, list) else [data]
        
    async def get_series_by_id(self, series_id: int) -> Series:
        """
        Получить информацию о конкретном аниме
        
        Args:
            series_id: ID аниме
            
        Returns:
            Информация об аниме
        """
        try:
            series_id = validate_id(series_id, "series_id")
        except ValueError as e:
            raise IDError(str(e))
            
        response = await self._make_request("GET", f"/series/{series_id}")
        data = SeriesResponse(**response).data
        return data if isinstance(data, Series) else data[0]
    
    async def search_anime(self, query: str, limit: int = 10) -> List[Series]:
        """
        Поиск аниме по названию
        
        Args:
            query: Поисковый запрос
            limit: Количество результатов
            
        Returns:
            Список найденных аниме
        """
        try:
            query = validate_query(query)
            limit = validate_limit(limit)
        except ValueError as e:
            raise QueryError(str(e))
            
        return await self.get_series(query=query, limit=limit)
    
    async def get_anime_by_mal_id(self, mal_id: int) -> List[Series]:
        """
        Получить аниме по ID MyAnimeList
        
        Args:
            mal_id: ID на MyAnimeList
            
        Returns:
            Список аниме (обычно один элемент)
        """
        try:
            mal_id = validate_id(mal_id, "mal_id")
        except ValueError as e:
            raise IDError(str(e))
            
        return await self.get_series(myAnimeListId=mal_id, limit=1)

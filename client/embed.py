"""
Модуль для работы с embed данными
"""

from .base import BaseClient
from ..exceptions.auth import AuthenticationError
from ..exceptions.validation import IDError
from ..utils import validate_id
from ..models import EmbedData, EmbedResponse


class EmbedMixin(BaseClient):
    """Миксин для работы с embed данными"""
    
    async def get_embed_data(self, translation_id: int) -> EmbedData:
        """
        Получить embed информацию для воспроизведения/скачивания
        
        Args:
            translation_id: ID перевода
            
        Returns:
            Embed данные
            
        Raises:
            AuthenticationError: Требуется авторизация
        """
        try:
            translation_id = validate_id(translation_id, "translation_id")
        except ValueError as e:
            raise IDError(str(e))
        
        if not self.access_token:
            raise AuthenticationError("Требуется авторизация для получения embed данных")
            
        response = await self._make_request(
            "GET", 
            f"/translations/embed/{translation_id}",
            require_auth=True
        )
        return EmbedResponse(**response).data

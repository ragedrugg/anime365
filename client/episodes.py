"""
Модуль для работы с эпизодами
"""

from .base import BaseClient
from ..exceptions.validation import IDError
from ..utils import validate_id
from ..models import Episode, EpisodeResponse


class EpisodesMixin(BaseClient):
    """Миксин для работы с эпизодами"""
    
    async def get_episode(self, episode_id: int) -> Episode:
        """
        Получить информацию об эпизоде
        
        Args:
            episode_id: ID эпизода
            
        Returns:
            Информация об эпизоде
        """
        try:
            episode_id = validate_id(episode_id, "episode_id")
        except ValueError as e:
            raise IDError(str(e))
            
        response = await self._make_request("GET", f"/episodes/{episode_id}")
        return EpisodeResponse(**response).data

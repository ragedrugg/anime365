"""
Модуль авторизации
"""

from typing import Optional
from .base import BaseClient
from ..exceptions.auth import AuthenticationError, LoginError
from ..utils import validate_token, validate_email, validate_password
from ..models import UserResponse, User


class AuthMixin(BaseClient):
    """Миксин для авторизации"""
    
    def __init__(self, *args, email: Optional[str] = None, password: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email
        self.password = password
    
    async def login(self) -> str:
        """
        Авторизация по email и паролю
        
        Returns:
            Токен доступа
            
        Raises:
            AuthenticationError: Ошибка авторизации
        """
        if not self.email or not self.password:
            raise AuthenticationError("Email и пароль не указаны")
        
        # Валидация email
        try:
            validate_email(self.email)
        except ValueError as e:
            raise AuthenticationError(str(e))
        
        # Валидация пароля
        try:
            validate_password(self.password)
        except ValueError as e:
            raise AuthenticationError(str(e))
            
        params = {
            "app": "universal",
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = await self._make_request("POST", "/login", params)
            
            if "access_token" not in response:
                raise AuthenticationError("Токен не получен")
            
            token = response["access_token"]
            try:
                validate_token(token)
            except ValueError as e:
                raise AuthenticationError(str(e))
                
            self.access_token = token
            return self.access_token
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            if "401" in str(e) or "unauthorized" in str(e).lower():
                raise LoginError("Неверный email или пароль")
            else:
                raise AuthenticationError(f"Ошибка авторизации: {e}")
    
    async def get_user_info(self) -> 'User':
        """
        Получить информацию о текущем пользователе
        
        Returns:
            Информация о пользователе
            
        Raises:
            AuthenticationError: Требуется авторизация
        """
        response = await self._make_request("GET", "/me", require_auth=True)
        return UserResponse(**response).data
    
    async def get_access_token_from_site(self) -> str:
        """
        Получить токен доступа через сайт (требует авторизации через браузер)
        
        Примечание: Этот метод требует предварительной авторизации через браузер
        на сайте https://smotret-anime.online/users/login
        
        Returns:
            Токен доступа
            
        Raises:
            AuthenticationError: Требуется авторизация через браузер
        """
        try:
            response = await self._make_request("GET", "/accessToken?app=universal")
            
            if "access_token" not in response:
                raise AuthenticationError("Токен не получен")
            
            token = response["access_token"]
            try:
                validate_token(token)
            except ValueError as e:
                raise AuthenticationError(str(e))
                
            self.access_token = token
            return self.access_token
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            else:
                raise AuthenticationError(f"Ошибка получения токена через сайт: {e}")

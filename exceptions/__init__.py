"""
Исключения для библиотеки
"""

from .base import Anime365Error, ValidationError, NetworkError
from .auth import AuthenticationError, TokenError, LoginError
from .api import APIError, NotFoundError, RateLimitError, ServerError, ClientError
from .validation import ParameterError, IDError, LimitError, QueryError

__all__ = [
    # Base exceptions
    "Anime365Error",
    "ValidationError", 
    "NetworkError",
    
    # Auth exceptions
    "AuthenticationError",
    "TokenError",
    "LoginError",
    
    # API exceptions
    "APIError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ClientError",
    
    # Validation exceptions
    "ParameterError",
    "IDError",
    "LimitError",
    "QueryError",
]

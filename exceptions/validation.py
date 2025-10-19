"""
Исключения для валидации
"""

from .base import ValidationError


class ParameterError(ValidationError):
    """Ошибка параметра"""
    pass


class IDError(ParameterError):
    """Ошибка ID"""
    pass


class LimitError(ParameterError):
    """Ошибка лимита"""
    pass


class QueryError(ParameterError):
    """Ошибка поискового запроса"""
    pass

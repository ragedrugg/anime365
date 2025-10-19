"""
Валидаторы для библиотеки anime365
"""

from typing import Any


def validate_id(value: Any, name: str = "ID") -> int:
    """Валидация ID"""
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} должен быть положительным числом")
    return value


def validate_limit(value: Any) -> int:
    """Валидация лимита"""
    if not isinstance(value, int):
        raise ValueError("limit должен быть числом")
    if value < 0 or value > 1000:
        raise ValueError("limit должен быть между 0 и 1000")
    return value


def validate_offset(value: Any) -> int:
    """Валидация смещения"""
    if not isinstance(value, int):
        raise ValueError("offset должен быть числом")
    if value < 0:
        raise ValueError("offset не может быть отрицательным")
    return value


def validate_query(value: Any) -> str:
    """Валидация поискового запроса"""
    if not isinstance(value, str):
        raise ValueError("query должен быть строкой")
    if not value or not value.strip():
        raise ValueError("query не может быть пустым")
    if len(value) > 1000:
        raise ValueError("query слишком длинный")
    return value.strip()


def validate_feed(value: Any) -> str:
    """Валидация типа ленты"""
    if not isinstance(value, str):
        raise ValueError("feed должен быть строкой")
    if value not in ["recent", "id", "all"]:
        raise ValueError("feed должен быть 'recent', 'id' или 'all'")
    return value


def validate_token(value: Any) -> str:
    """Валидация токена"""
    if not isinstance(value, str):
        raise ValueError("access_token должен быть строкой")
    if len(value) < 10:
        raise ValueError("access_token должен быть строкой длиной не менее 10 символов")
    return value


def validate_email(value: Any) -> str:
    """Валидация email"""
    if not isinstance(value, str):
        raise ValueError("email должен быть строкой")
    if "@" not in value or len(value) < 5:
        raise ValueError("Неверный формат email")
    return value


def validate_password(value: Any) -> str:
    """Валидация пароля"""
    if not isinstance(value, str):
        raise ValueError("password должен быть строкой")
    if len(value) < 3:
        raise ValueError("Пароль слишком короткий")
    return value

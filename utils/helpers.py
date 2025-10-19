"""
Вспомогательные функции для библиотеки anime365
"""

import asyncio
import random
from typing import Dict, Any, Optional


def build_params(**kwargs) -> Dict[str, Any]:
    """Построение параметров запроса"""
    params = {}
    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, list):
                params[key] = ",".join(str(v) for v in value)
            else:
                params[key] = value
    return params


def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """Расчет задержки для retry с экспоненциальным backoff и jitter"""
    delay = base_delay * (2 ** attempt)
    jitter = random.uniform(0, 1)
    return delay + jitter


async def sleep_with_jitter(delay: float) -> None:
    """Задержка с небольшим случайным отклонением"""
    jitter = random.uniform(0, 0.1)
    await asyncio.sleep(delay + jitter)


def format_error_message(status_code: int, response_text: str) -> str:
    """Форматирование сообщения об ошибке"""
    if status_code == 401:
        return "Неверный токен авторизации"
    elif status_code == 403:
        return "Доступ запрещен"
    elif status_code == 404:
        return "Ресурс не найден"
    elif status_code == 414:
        return "Запрос слишком длинный"
    elif status_code == 429:
        return "Превышен лимит запросов"
    elif status_code >= 500:
        return f"Ошибка сервера (HTTP {status_code})"
    elif status_code >= 400:
        return f"Ошибка клиента (HTTP {status_code})"
    else:
        return f"Неизвестная ошибка (HTTP {status_code})"


def extract_api_error(response_data: Dict[str, Any]) -> Optional[str]:
    """Извлечение ошибки из ответа API"""
    if isinstance(response_data, dict) and "error" in response_data:
        error_info = response_data["error"]
        if isinstance(error_info, dict) and "code" in error_info:
            code = error_info["code"]
            message = error_info.get("message", "Неизвестная ошибка")
            if code == 404:
                return "Ресурс не найден"
            else:
                return f"API ошибка {code}: {message}"
    return None

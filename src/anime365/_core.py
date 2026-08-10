"""Транспорт-агностичная логика, общая для sync- и async-клиента.

Ни один из объектов в этом модуле не выполняет ввод-вывод — это позволяет
``Anime365`` и ``AsyncAnime365`` полагаться на одну и ту же логику разбора
ответов, сборки параметров и расчёта задержки повторов, не расходясь в
поведении.
"""

from __future__ import annotations

import random
from typing import Any
from urllib.parse import urljoin

from .errors import Anime365Error

DEFAULT_MIRRORS: tuple[str, ...] = (
    "https://smotret-anime.app/api",
    "https://smotret-anime.online/api",
    "https://smotret-anime.org/api",
    "https://anime365.ru/api",
    "https://anime-365.ru/api",
)
"""Известные домены-зеркала anime365. Пробуются по порядку при сетевых сбоях."""


def build_params(**kwargs: Any) -> dict[str, str]:
    """Строит query-параметры из именованных аргументов.

    ``None`` пропускается, списки склеиваются через запятую, булевы значения
    приводятся к ``"1"``/``"0"``.
    """
    params: dict[str, str] = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, bool):
            params[key] = "1" if value else "0"
        elif isinstance(value, (list, tuple)):
            params[key] = ",".join(str(v) for v in value)
        else:
            params[key] = str(value)
    return params


def parse_payload(json: dict[str, Any]) -> Any:
    """Разбирает тело ответа API: возвращает ``data`` либо поднимает ``Anime365Error``."""
    error = json.get("error")
    if error is not None:
        raise Anime365Error(error.get("code"), error.get("message"), error.get("fields"))
    return json.get("data")


def retry_delay(attempt: int, base: float) -> float:
    """Экспоненциальный бэкофф с джиттером для попытки ``attempt`` (0-based)."""
    return float(base * (2**attempt) * (0.5 + random.random() / 2))


def absolutize(base_url: str, url: str) -> str:
    """Приводит потенциально относительный ``url`` к абсолютному относительно ``base_url``."""
    return urljoin(base_url, url)

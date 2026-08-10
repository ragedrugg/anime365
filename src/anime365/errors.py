"""Исключения клиента."""

from __future__ import annotations


class Anime365Error(Exception):
    """Ошибка, возвращаемая API anime365.

    API всегда отвечает HTTP 200 и кодирует ошибки в теле как
    ``{"error": {"code", "message", "fields"?}}`` — эта проверка не сводится
    к ``response.status_code``, поэтому клиент разбирает тело ответа.
    """

    def __init__(self, code: int, message: str, fields: dict[str, list[str]] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.fields = fields

    def __repr__(self) -> str:
        return f"Anime365Error(code={self.code!r}, message={self.message!r}, fields={self.fields!r})"


class Anime365NetworkError(Exception):
    """Сетевая ошибка транспортного уровня (таймаут, DNS, недоступность хоста и т.д.)."""

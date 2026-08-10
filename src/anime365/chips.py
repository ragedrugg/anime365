"""Расширенный фильтр каталога (`chips`).

Одно условие вида ``ChipCondition(field="genre", operator="@=", value=[8, 35])``
превращается в ``"genre@=8,35"`` — так же, как в URL каталога сайта
(``https://smotret-anime.online/catalog/filter/genre@=8,35;genre_op=and``).

API не публикует список допустимых полей/операторов, поэтому эта функция
ничего не проверяет и не подставляет — она лишь механически собирает строку.
Актуальные варианты нужно подсматривать на сайте (вкладка фильтров).
"""

from __future__ import annotations

from dataclasses import dataclass

ChipValue = str | int | list[str | int]


@dataclass
class ChipCondition:
    field: str
    operator: str
    value: ChipValue


Chip = ChipCondition | str


def _stringify(chip: Chip) -> str:
    if isinstance(chip, str):
        return chip
    value = ",".join(str(v) for v in chip.value) if isinstance(chip.value, list) else str(chip.value)
    return f"{chip.field}{chip.operator}{value}"


def build_chips(chips: list[Chip]) -> str:
    """Собирает значение параметра ``chips`` из списка условий, разделяя их ``;``."""
    return ";".join(_stringify(chip) for chip in chips)

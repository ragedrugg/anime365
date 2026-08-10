"""Постраничный проход по всему каталогу через iterate_series() — под капотом идёт
по afterId, а не offset (так рекомендует документация API на больших списках).

Запуск: python examples/iterate_catalog.py
"""

from anime365 import Anime365

api = Anime365(user_agent="ExampleApp/1.0")

total = 0
for series in api.iterate_series(limit=200):
    total += 1
    if total <= 5:
        print(f"#{series.id} {series.title} ({series.year})")

print(f"Всего аниме в каталоге: {total}")

"""Полное сканирование ленты переводов через iterate_translations() (feed="id" — сначала
самые старые записи, удобно для полного сканирования).

Запуск: python examples/full_scan.py
"""

from anime365 import Anime365

api = Anime365(user_agent="ExampleApp/1.0")

total = 0
LIMIT = 600  # в реальном сканировании убрать ограничение и идти до конца ленты
for _translation in api.iterate_translations(feed="id", limit=200):
    total += 1
    if total >= LIMIT:
        break

print(f"Всего обработано: {total}")

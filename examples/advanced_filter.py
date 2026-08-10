"""Расширенный фильтр каталога через build_chips() — аналог фильтра на сайте
https://smotret-anime.app/catalog/filter/genre@=8,35;genre_op=and

Запуск: python examples/advanced_filter.py
"""

from anime365 import Anime365, ChipCondition, build_chips

api = Anime365(user_agent="ExampleApp/1.0")

chips = build_chips([ChipCondition(field="genre", operator="@=", value=[8, 35]), "genre_op=and"])
print("chips:", chips)

results = api.get_series(chips=chips, fields=["id", "title"], limit=10)
for series in results:
    print(f"#{series.id} {series.title}")

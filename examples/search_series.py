"""Поиск аниме по названию и вывод основных полей.

Запуск: python examples/search_series.py "gate"
"""

import sys

from anime365 import Anime365

api = Anime365(user_agent="ExampleApp/1.0")
query = sys.argv[1] if len(sys.argv) > 1 else "gate"

results = api.get_series(query=query, fields=["id", "title", "typeTitle", "year", "posterUrlSmall"], limit=10)
for series in results:
    print(f"#{series.id} {series.title} — {series.type_title}, {series.year}")

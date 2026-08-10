"""То же самое, что search_series.py, но на асинхронном клиенте AsyncAnime365 —
удобно, когда запросы к API идут параллельно с остальной asyncio-программой.

Запуск: python examples/async_search_series.py "gate"
"""

import asyncio
import sys

from anime365 import AsyncAnime365


async def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "gate"
    async with AsyncAnime365(user_agent="ExampleApp/1.0") as api:
        results = await api.get_series(query=query, fields=["id", "title", "typeTitle", "year"], limit=10)
    for series in results:
        print(f"#{series.id} {series.title} — {series.type_title}, {series.year}")


asyncio.run(main())

"""Последние добавленные переводы онгоингов.

Запуск: python examples/recent_translations.py
"""

from anime365 import Anime365

api = Anime365(user_agent="ExampleApp/1.0")

translations = api.get_translations(feed="recent")
for t in translations[:20]:
    print(f"[{t.type_kind}/{t.type_lang}] {t.title} — {t.authors_summary}")

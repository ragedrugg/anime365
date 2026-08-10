"""Вход по email/паролю (или готовому токену) и получение ссылок на видео/субтитры перевода.

Запуск: ANIME365_TOKEN=... python examples/login_and_embed.py [translation_id]
    или: ANIME_EMAIL=... ANIME_PASSWORD=... python examples/login_and_embed.py [translation_id]
"""

import os
import sys

from anime365 import Anime365

ANIME_EMAIL = os.environ.get("ANIME_EMAIL")
ANIME_PASSWORD = os.environ.get("ANIME_PASSWORD")
ANIME365_TOKEN = os.environ.get("ANIME365_TOKEN")
translation_id = int(sys.argv[1]) if len(sys.argv) > 1 else 905760

api = Anime365(user_agent="ExampleApp/1.0")

if ANIME365_TOKEN:
    api.access_token = ANIME365_TOKEN
elif ANIME_EMAIL and ANIME_PASSWORD:
    api.login(ANIME_EMAIL, ANIME_PASSWORD)
else:
    print("Укажите ANIME365_TOKEN либо ANIME_EMAIL/ANIME_PASSWORD", file=sys.stderr)
    sys.exit(1)

user = api.get_me()
print(f"Вошли как {user.name} (id={user.id}, premium={user.is_premium})")

embed = api.get_translation_embed(translation_id)
print("Субтитры (ASS):", embed.subtitles_url)
for stream in embed.stream:
    print(f"Поток {stream.height}p:", stream.urls[0])

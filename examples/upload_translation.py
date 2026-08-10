"""Полный флоу добавления перевода: логин, загрузка видео (+опционально субтитров) по tus
и создание перевода — так же, как форма добавления на сайте.

Запуск: ANIME_EMAIL=... ANIME_PASSWORD=... \
    python examples/upload_translation.py <video.mp4> [subtitles.ass]
"""

import os
import sys

from anime365 import Anime365
from anime365.upload import add_translation, file_source

ANIME_EMAIL = os.environ.get("ANIME_EMAIL")
ANIME_PASSWORD = os.environ.get("ANIME_PASSWORD")
ANIME365_TOKEN = os.environ.get("ANIME365_TOKEN")

args = sys.argv[1:]
if not args:
    print("Использование: upload_translation.py <video.mp4> [subtitles.ass]", file=sys.stderr)
    sys.exit(1)

api = Anime365(user_agent="ExampleApp/1.0")

if ANIME365_TOKEN:
    api.access_token = ANIME365_TOKEN
elif ANIME_EMAIL and ANIME_PASSWORD:
    api.login(ANIME_EMAIL, ANIME_PASSWORD)
else:
    print("Укажите ANIME365_TOKEN либо ANIME_EMAIL/ANIME_PASSWORD", file=sys.stderr)
    sys.exit(1)

video = file_source(args[0])
subtitles = file_source(args[1]) if len(args) > 1 else None


def on_progress(uploaded: int, total: int) -> None:
    print(f"\rВидео: {uploaded / total * 100:.1f}%", end="", flush=True)


translation = add_translation(
    api,
    series_id=8245,
    episode_number=3,
    episode_type="tv",
    type="voiceRu",
    authors="Author1 & Author2",
    video=video,
    subtitles=subtitles,
    on_video_progress=on_progress,
)
print(f"\nПеревод создан: {translation.url}")

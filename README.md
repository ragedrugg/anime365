# Anime365

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI Version](https://img.shields.io/badge/pypi-1.0.0-orange.svg)](https://pypi.org/project/anime365/)
[![Downloads](https://img.shields.io/badge/downloads-monthly-brightgreen.svg)](https://pypi.org/project/anime365/)
[![Status](https://img.shields.io/badge/status-stable-success.svg)](https://github.com/ragedrugg/anime365)

Асинхронная Python библиотека для работы с API сайта [Anime365](https://smotret-anime.online).

## Установка

```bash
pip install anime365
```

## Быстрый старт

```python
import asyncio
from anime365 import Anime365Client

async def main():
    client = Anime365Client(access_token="<token>")
    
    try:
        # Информация о пользователе
        user = await client.get_user_info()
        print(f"Пользователь: {user.name}")
        
        # Поиск аниме
        anime_list = await client.search_anime("naruto", limit=5)
        for anime in anime_list:
            print(f"- {anime.title} ({anime.year})")
        
        # Последние переводы
        translations = await client.get_recent_translations(limit=3)
        for trans in translations:
            print(f"- {trans.title}")
            
    finally:
        await client.close()

asyncio.run(main())
```

## Основные функции

```python
# Поиск аниме
anime = await client.search_anime("attack on titan", limit=10)

# Получение переводов
translations = await client.get_anime_translations(anime_id, limit=100)

# Embed данные для воспроизведения
embed_data = await client.get_embed_data(translation_id)

# Информация об эпизоде
episode = await client.get_episode(episode_id)
```

## Авторизация

```python
# Через токен
client = Anime365Client(access_token="<token>")

# Через email/пароль
client = Anime365Client(
    email="email@example.com",
    password="password"
)
```

## Требования

- Python 3.7+
- aiohttp >= 3.8.0
- pydantic >= 2.0.0

## Лицензия

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MIT License

## Поддержка

Для получения документации API обратитесь к модерации сайта Anime365.

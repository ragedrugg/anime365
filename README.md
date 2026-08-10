# anime365

<p align="center">
  <img src="./assets/banner.png" alt="anime365" width="100%" />
</p>

Python-клиент для API [anime365](https://anime-365.ru/api-docs) (домены smotret-anime.app /
.online / .org, anime365.ru, anime-365.ru): каталог аниме, эпизоды, переводы (озвучки и
субтитры), ссылки на видео/субтитры, авторизация и загрузка видео (tus). Полностью покрывает
официальную OpenAPI-спеку (продублирована в [`openapi.yaml`](./openapi.yaml)). Два клиента на
[httpx](https://www.python-httpx.org/) с одинаковой поверхностью — `Anime365` (sync) и
`AsyncAnime365` (async).

## Требования

- Python 3.10+
- httpx, pydantic v2

## Установка

```bash
pip install anime365
```

## Быстрый старт

```python
from anime365 import Anime365

api = Anime365(user_agent="MyApp/1.0")

series = api.get_series(query="gate", limit=10)
translations = api.get_translations(feed="recent")
```

Или асинхронно:

```python
import asyncio
from anime365 import AsyncAnime365


async def main() -> None:
    async with AsyncAnime365(user_agent="MyApp/1.0") as api:
        series = await api.get_series(query="gate", limit=10)


asyncio.run(main())
```

API просит всегда указывать `user_agent` — название сайта или программы.

## Особенности API, которые важно знать

- **Ошибки приходят с HTTP 200.** Тело ответа при ошибке — `{"error": {"code", "message", "fields"?}}`,
  статус при этом не меняется. Библиотека разбирает это сама и поднимает `Anime365Error` —
  проверять код статуса ответа бессмысленно, полагайтесь на `try/except`.
- **Для полного сканирования используйте `after_id`, а не `offset`.** При счёте на сотни тысяч
  записей `offset` работает медленно. Для этого есть готовые итераторы —
  `iterate_series`/`iterate_episodes`/`iterate_translations`, см. ниже.
- **`subtitles_url` из `get_translation_embed()` бывает относительным** (например
  `/episodeTranslations/123.ass?willcache`). Библиотека сама приводит его к абсолютному URL
  относительно текущего зеркала.
- **У `access_token` нет срока действия** — он действителен, пока не сменится пароль. Храните
  его как секрет (переменная окружения, секрет-хранилище), не коммитьте в репозиторий.
- **Домен API может меняться и блокироваться регионально** — у сервиса несколько официальных
  зеркал. По умолчанию библиотека пробует их все по очереди при сетевых сбоях — см. «Зеркала и
  fallback» ниже.

## Конструктор

Одинаковые параметры у `Anime365` и `AsyncAnime365`:

```python
Anime365(
    base_url=None,          # str | list[str] | None — по умолчанию DEFAULT_MIRRORS (все известные зеркала)
    user_agent="anime365/2.0",
    access_token=None,      # если токен уже известен
    app="universal",        # идентификатор API-клиента для login/fetch_access_token
    timeout=30.0,            # таймаут одной попытки запроса, секунды
    retries=2,                # повторы на одном зеркале при сетевых сбоях/5xx
    retry_delay_base=0.3,    # базовая задержка перед повтором (экспоненциально растёт), секунды
    client=None,               # свой httpx.Client / httpx.AsyncClient — для тестов/прокси
)
```

## Зеркала и fallback

По умолчанию (`base_url` не указан) используется список `DEFAULT_MIRRORS` — все известные
домены anime365 в порядке приоритета. При сетевом сбое (недоступный домен, DNS, таймаут, 5xx)
запрос сначала повторяется на том же зеркале (`retries` раз), а затем библиотека пробует
следующее зеркало из списка. Ошибки самого API (`Anime365Error`, например 404 или неверный
пароль) ни повтор, ни fallback не запускают — домен ответил, значит проблема не в нём. Зеркало,
на котором прошёл последний успешный запрос, запоминается и используется первым в следующий раз.

```python
from anime365 import DEFAULT_MIRRORS, Anime365

print(DEFAULT_MIRRORS)  # ('https://smotret-anime.app/api', 'https://smotret-anime.online/api', ...)

api = Anime365()  # fallback по всем зеркалам сразу из коробки
print(api.active_base_url)  # текущее рабочее зеркало

# base_url строкой — фиксированный домен без fallback
pinned = Anime365(base_url="https://smotret-anime.app/api")

# свой список зеркал
custom = Anime365(base_url=["https://smotret-anime.online/api", "https://anime365.ru/api"])
```

## Авторизация

```python
from anime365 import Anime365

api = Anime365(user_agent="MyApp/1.0")

token = api.login("user@example.com", "password")  # сохраняется в клиенте
me = api.get_me()  # User(is_logined=True, id=..., name=..., is_premium=..., premium_until=...)

# либо переиспользовать уже полученный токен
api.access_token = token
```

Получить `access_token` можно и вручную на сайте: `api.social_login_url` (вход по
email/паролю или через соцсети). Если пользователь уже вошёл на сайте (например, в браузере),
токен для вашего `app` выдаёт `fetch_access_token()`:

```python
token = api.fetch_access_token()  # требует активной сессии в куках браузера
```

`app` — идентификатор зарегистрированного API-клиента (не секрет, можно публиковать в открытом
коде). По умолчанию используется `"universal"`; свой можно зарегистрировать на странице
[создания API-клиента](https://smotret-anime.app/api/clients) и передать через
`Anime365(app="мой-клиент")`.

## Методы

Все методы `Anime365` есть и у `AsyncAnime365` — просто с `await`.

### Каталог

```python
get_series(
    limit=None, offset=None, fields=None,  # fields: str | Iterable[str]
    query=None,                             # поиск по названию
    chips=None,                             # расширенный фильтр каталога, см. build_chips() ниже
    after_id=None, order=None,              # order="id"
    my_anime_list_id=None, is_active=None, is_airing=None,
    type=None,                              # tv, movie, ova, ona, special, music
    year=None, season=None,
) -> list[Series]

get_series_by_id(series_id, *, fields=None) -> Series

get_episodes(
    limit=None, offset=None, fields=None,
    series_id=None, episode_int=None, episode_type=None,
    is_active=None, is_first_uploaded=None, after_id=None,
) -> list[Episode]

get_episode_by_id(episode_id, *, fields=None) -> Episode

get_video_by_id(video_id) -> Video
```

### Переводы

```python
get_translations(
    limit=None, offset=None, fields=None,
    series_id=None, episode_id=None,
    feed=None,        # recent, id, all, updatedDateTime, addedDateTime
    after_id=None,
    type=None,        # voiceRu, subRu, voiceEn, subEn, raw...
    quality_type=None, is_active=None,
) -> list[Translation]

get_translation_by_id(translation_id, *, fields=None) -> Translation

get_translation_embed(translation_id) -> EmbedTranslation  # ссылки на видео/субтитры, требует авторизации
```

### Аккаунт

```python
get_me() -> User                                 # требует access_token
login(email, password) -> str                    # возвращает и сохраняет access_token
fetch_access_token() -> str                       # токен для текущей сессии на сайте
```

### Загрузка видео

```python
get_upload_endpoints() -> UploadEndpoints         # доступные tus-каналы и рекомендуемый
create_translation(payload: TranslationCreateRequest) -> Translation
```

### Прямой доступ к API

```python
request(path, params=None, *, method="GET", json=None) -> Any
```

Escape hatch для эндпоинтов, которых ещё нет в типизированных методах — работает через тот же
транспорт (fallback по зеркалам, повторы, разбор `{error}`).

## Постраничные итераторы

Для полного сканирования больших списков — генераторы, которые сами проходят страницы через
`after_id` (как требует документация вместо `offset`):

```python
for series in api.iterate_series(fields=["id", "title"]):
    print(series.id, series.title)

for translation in api.iterate_translations(feed="id"):
    ...

for episode in api.iterate_episodes(series_id=30414):
    ...
```

В `AsyncAnime365` — те же методы как асинхронные генераторы (`async for`).

## Расширенный фильтр каталога (`chips`)

Список допустимых полей и операторов сам API не публикует — их видно только на сайте (вкладка
фильтров каталога) или в `site.ccsData` исходного кода страницы `/catalog`. `build_chips()` лишь
механически собирает строку в формате, который использует сайт, ничего не проверяя:

```python
from anime365 import Anime365, ChipCondition, build_chips

chips = build_chips([ChipCondition(field="genre", operator="@=", value=[8, 35]), "genre_op=and"])
# chips == "genre@=8,35;genre_op=and"

api = Anime365()
results = api.get_series(chips=chips)
# либо передать список условий напрямую — build_chips() вызовется внутри
results = api.get_series(chips=[ChipCondition(field="genre", operator="@=", value=[8, 35])])
```

## Загрузка видео и добавление перевода

Протокол — [tus 1.0.0](https://tus.io). Библиотека включает минимальный tus-клиент (sync и
async, без сторонних зависимостей сверх httpx/anyio) и высокоуровневый флоу `add_translation()`:

```python
from anime365 import Anime365
from anime365.upload import add_translation, file_source

api = Anime365(user_agent="MyApp/1.0")
api.login("user@example.com", "password")

translation = add_translation(
    api,
    series_id=8245,
    episode_number=3,
    episode_type="tv",
    type="voiceRu",
    authors="Author1 & Author2",
    video=file_source("./episode-03.mp4"),
    subtitles=file_source("./episode-03.ass"),  # необязательно
    compute_sha256=True,  # посчитать и передать sha256 для проверки целостности
    on_video_progress=lambda uploaded, total: print(f"{uploaded / total * 100:.1f}%"),
)

print(translation.url)
```

Асинхронный вариант — `anime365.upload.add_translation_async()` с `AsyncAnime365`.

`add_translation()` сам получает точки загрузки (`get_upload_endpoints()`), выбирает
рекомендованный канал (с фолбэком по всем его адресам), заливает видео и субтитры по tus и
создаёт перевод через `create_translation()`.

Более низкоуровневые примитивы — `upload_to_channel()`/`upload_to_channel_async()` (одна
загрузка на конкретный канал, с поддержкой докачки через `resume_uuid`), `file_source()`
(источник из файла на диске, читается по смещению без загрузки в память) и `bytes_source()`
(источник из буфера в памяти).

## Обработка ошибок

```python
from anime365 import Anime365, Anime365Error, Anime365NetworkError

api = Anime365()

try:
    api.get_series_by_id(999999999)
except Anime365Error as error:
    print(f"API вернул ошибку {error.code}: {error.message}")  # 404: Series not found.
    if error.fields:
        print(error.fields)  # ошибки валидации create_translation()
except Anime365NetworkError as error:
    print("Сеть недоступна или ответ не удалось разобрать:", error)
```

## Модели

Модели — pydantic v2, поля в snake_case (`series.poster_url`, `episode.episode_int`), но
принимают и сырой camelCase JSON от API напрямую (`Series(**raw_json)`), а неизвестные API
добавит в будущем поля не приводят к ошибке:

```python
from anime365 import (
    Series, Episode, Translation, Video, EmbedTranslation, User,
    UploadEndpoint, UploadEndpoints, TranslationCreateRequest,
    DownloadOption, StreamOption, AccessTokenResponse,
)
```

Справочные словари с русскоязычными подписями значений (`ANIME_TYPES`, `TRANSLATION_TYPES`,
`LANGUAGE_TYPES` и т.д.) — в `anime365.constants`.

## Примеры

В каталоге [`examples/`](./examples) — рабочие скрипты: поиск аниме (sync и async), лента
последних переводов, полное сканирование переводов и каталога через итераторы, авторизация +
получение embed-данных, расширенный фильтр через `build_chips()`, загрузка видео и создание
перевода.

```bash
python examples/search_series.py gate
python examples/async_search_series.py gate
```

## Миграция с 1.x

Версия 2.0 — чистый релиз без легаси-алиасов, покрывает всю официальную OpenAPI-спеку (в 1.x
было 8 эндпоинтов из 13, без `/episodes`, `/videos/{id}`, `/upload/endpoints`,
`POST /translations/create`).

| 1.x | 2.0 |
| --- | --- |
| `Anime365Client` (только async, aiohttp) | `Anime365` (sync) и `AsyncAnime365` (async), оба на httpx |
| `search_anime()` / `get_anime_by_mal_id()` | `get_series(query=...)` / `get_series(my_anime_list_id=...)` |
| `get_anime_translations()` | `get_translations(series_id=...)` |
| `get_embed_data()` | `get_translation_embed()` |
| `get_series()` без части параметров | `get_series()` — все параметры спеки: `chips`, `after_id`, `order`, `is_active`, `is_airing`, `type`, `year`, `season` |
| 14 классов исключений | `Anime365Error` (ошибки API, `code`/`message`/`fields`) и `Anime365NetworkError` (сетевые) |
| единственный домен `smotret-anime.online` | fallback по 5 зеркалам с ретраями |

Новое в 2.0: `get_episodes()`, `get_video_by_id()`, `fetch_access_token()`,
`get_upload_endpoints()`, `create_translation()`/`add_translation()` (загрузка видео по tus),
итераторы `iterate_series`/`iterate_episodes`/`iterate_translations`, `build_chips()`, ретраи с
бэкоффом и fallback по зеркалам, `error.fields` в `Anime365Error`.

## Разработка

```bash
git clone https://github.com/ragedrugg/anime365.git
cd anime365
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                 # юнит-тесты (pytest + respx, мок httpx)
ruff check src tests examples
mypy src
```

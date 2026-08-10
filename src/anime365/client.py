"""Клиенты API anime365: `Anime365` (sync) и `AsyncAnime365` (async), оба на httpx."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Iterable, Iterator
from typing import Any, Literal

import httpx

from ._core import DEFAULT_MIRRORS, absolutize, build_params, parse_payload, retry_delay
from .chips import Chip, build_chips
from .errors import Anime365NetworkError
from .models import (
    AccessTokenResponse,
    EmbedTranslation,
    Episode,
    Series,
    Translation,
    TranslationCreateRequest,
    UploadEndpoints,
    User,
    Video,
)

FieldsParam = str | Iterable[str] | None
ChipsParam = str | list[Chip] | None


def _resolve_chips(chips: ChipsParam) -> str | None:
    if chips is None or isinstance(chips, str):
        return chips
    return build_chips(chips)


class _Anime365Base:
    """Общая конфигурация и чистые (без ввода-вывода) вспомогательные методы."""

    def __init__(
        self,
        base_url: str | Iterable[str] | None = None,
        *,
        user_agent: str = "anime365/2.0",
        access_token: str | None = None,
        app: str = "universal",
        timeout: float = 30.0,
        retries: int = 2,
        retry_delay_base: float = 0.3,
    ) -> None:
        raw = list(base_url) if base_url is not None else list(DEFAULT_MIRRORS)
        if isinstance(base_url, str):
            raw = [base_url]
        self._mirrors = [url.rstrip("/") for url in raw]
        if not self._mirrors:
            raise ValueError("base_url: список зеркал не может быть пустым")
        self._active_mirror_index = 0
        self.user_agent = user_agent
        self.access_token = access_token
        self.app = app
        self.timeout = timeout
        self.retries = retries
        self.retry_delay_base = retry_delay_base

    @property
    def active_base_url(self) -> str:
        """Зеркало, использованное последним успешным запросом (или первое из списка)."""
        return self._mirrors[self._active_mirror_index]

    @property
    def available_mirrors(self) -> list[str]:
        return list(self._mirrors)

    @property
    def _site_url(self) -> str:
        base = self.active_base_url
        return base[: -len("/api")] if base.endswith("/api") else base

    @property
    def social_login_url(self) -> str:
        """Страница входа через email/пароль или соцсети — там же можно получить access_token вручную."""
        return f"{self._site_url}/users/login"

    def _mirror_order(self) -> list[str]:
        """Порядок опроса зеркал для текущего запроса: начиная с последнего успешного, по кругу."""
        i = self._active_mirror_index
        return [*self._mirrors[i:], *self._mirrors[:i]]

    def _build_params(self, mirror: str, params: dict[str, Any] | None) -> dict[str, str]:
        merged = dict(params or {})
        if self.access_token:
            merged["access_token"] = self.access_token
        return build_params(**merged)

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent, "Accept": "application/json"}


class Anime365(_Anime365Base):
    """Синхронный клиент API anime365 (домены smotret-anime.app / .online / .org, anime365.ru, anime-365.ru)."""

    def __init__(self, *args: Any, client: httpx.Client | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = client or httpx.Client(timeout=self.timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Anime365:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ===== Транспорт =====

    def request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        method: str = "GET",
        json: Any = None,
    ) -> Any:
        """Универсальный escape hatch для эндпоинтов, которых нет в типизированных методах ниже."""
        order = self._mirror_order()
        last_error: Anime365NetworkError | None = None
        failed_mirrors: list[str] = []

        for mirror in order:
            try:
                result = self._request_with_retries(mirror, path, params, method=method, json=json)
                self._active_mirror_index = self._mirrors.index(mirror)
                return result
            except Anime365NetworkError as err:
                last_error = err
                failed_mirrors.append(mirror)
                continue

        raise Anime365NetworkError(
            f"Не удалось подключиться ни к одному из зеркал API ({', '.join(failed_mirrors)}): {last_error}"
        )

    def _request_with_retries(
        self, mirror: str, path: str, params: dict[str, Any] | None, *, method: str, json: Any
    ) -> Any:
        last_error: Anime365NetworkError | None = None
        for attempt in range(self.retries + 1):
            if attempt > 0:
                time.sleep(retry_delay(attempt - 1, self.retry_delay_base))
            try:
                return self._request_once(mirror, path, params, method=method, json=json)
            except Anime365NetworkError as err:
                last_error = err
                continue
        assert last_error is not None
        raise last_error

    def _request_once(
        self, mirror: str, path: str, params: dict[str, Any] | None, *, method: str, json: Any
    ) -> Any:
        url = f"{mirror}{path}"
        query = self._build_params(mirror, params)
        try:
            response = self._client.request(method, url, params=query, headers=self._headers(), json=json)
        except httpx.HTTPError as cause:
            raise Anime365NetworkError(f"Не удалось выполнить запрос к {url}: {cause}") from cause

        if response.status_code >= 500:
            raise Anime365NetworkError(f"Сервер {mirror} ответил {response.status_code} {response.reason_phrase}")

        try:
            payload = response.json()
        except ValueError as cause:
            raise Anime365NetworkError(
                f"Не удалось разобрать ответ API ({response.status_code} {response.reason_phrase})"
            ) from cause

        return parse_payload(payload)

    # ===== Аккаунт =====

    def login(self, email: str, password: str) -> str:
        """Авторизация по email и паролю. При успехе access_token сохраняется в клиенте."""
        data = self.request("/login", {"app": self.app, "email": email, "password": password})
        token = AccessTokenResponse.model_validate(data).access_token
        self.access_token = token
        return token

    def fetch_access_token(self) -> str:
        """Выдаёт access_token для пользователя, уже вошедшего на сайте (в браузере), под текущий app."""
        data = self.request("/accessToken", {"app": self.app})
        token = AccessTokenResponse.model_validate(data).access_token
        self.access_token = token
        return token

    def get_me(self) -> User:
        """Аккаунт, связанный с текущим access_token. Для гостей isLogined=False."""
        return User.model_validate(self.request("/me"))

    # ===== Каталог =====

    def get_series(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        query: str | None = None,
        chips: ChipsParam = None,
        after_id: int | None = None,
        order: Literal["id"] | None = None,
        my_anime_list_id: int | None = None,
        is_active: Literal[0, 1] | None = None,
        is_airing: Literal[0, 1] | None = None,
        type: str | None = None,
        year: int | None = None,
        season: str | None = None,
    ) -> list[Series]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "query": query,
            "chips": _resolve_chips(chips),
            "afterId": after_id,
            "order": order,
            "myAnimeListId": my_anime_list_id,
            "isActive": is_active,
            "isAiring": is_airing,
            "type": type,
            "year": year,
            "season": season,
        }
        return [Series.model_validate(item) for item in self.request("/series", params)]

    def get_series_by_id(self, series_id: int, *, fields: FieldsParam = None) -> Series:
        return Series.model_validate(self.request(f"/series/{series_id}", {"fields": fields}))

    def get_episodes(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        series_id: int | None = None,
        episode_int: float | str | None = None,
        episode_type: Literal["tv", "movie", "ova", "ona", "special"] | None = None,
        is_active: Literal[0, 1] | None = None,
        is_first_uploaded: Literal[0, 1] | None = None,
        after_id: int | None = None,
    ) -> list[Episode]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "seriesId": series_id,
            "episodeInt": episode_int,
            "episodeType": episode_type,
            "isActive": is_active,
            "isFirstUploaded": is_first_uploaded,
            "afterId": after_id,
        }
        return [Episode.model_validate(item) for item in self.request("/episodes", params)]

    def get_episode_by_id(self, episode_id: int, *, fields: FieldsParam = None) -> Episode:
        return Episode.model_validate(self.request(f"/episodes/{episode_id}", {"fields": fields}))

    def get_video_by_id(self, video_id: int) -> Video:
        return Video.model_validate(self.request(f"/videos/{video_id}"))

    # ===== Переводы =====

    def get_translations(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        series_id: int | None = None,
        episode_id: int | None = None,
        feed: Literal["recent", "id", "all", "updatedDateTime", "addedDateTime"] | None = None,
        after_id: int | None = None,
        type: str | None = None,
        quality_type: str | None = None,
        is_active: Literal[0, 1] | None = None,
    ) -> list[Translation]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "seriesId": series_id,
            "episodeId": episode_id,
            "feed": feed,
            "afterId": after_id,
            "type": type,
            "qualityType": quality_type,
            "isActive": is_active,
        }
        return [Translation.model_validate(item) for item in self.request("/translations", params)]

    def get_translation_by_id(self, translation_id: int, *, fields: FieldsParam = None) -> Translation:
        return Translation.model_validate(self.request(f"/translations/{translation_id}", {"fields": fields}))

    def get_translation_embed(self, translation_id: int) -> EmbedTranslation:
        """Ссылки на видео/субтитры для воспроизведения. Требует access_token с активной подпиской."""
        embed = EmbedTranslation.model_validate(self.request(f"/translations/embed/{translation_id}"))
        if embed.subtitles_url:
            embed.subtitles_url = absolutize(self._site_url, embed.subtitles_url)
        return embed

    # ===== Загрузка видео =====

    def get_upload_endpoints(self) -> UploadEndpoints:
        """Доступные точки загрузки (tus) и рекомендуемый для вас канал."""
        return UploadEndpoints.model_validate(self.request("/upload/endpoints"))

    def create_translation(self, payload: TranslationCreateRequest) -> Translation:
        """Создаёт перевод из уже загруженного по tus видео (см. anime365.upload)."""
        body = payload.model_dump(by_alias=True, exclude_none=True)
        return Translation.model_validate(self.request("/translations/create", method="POST", json=body))

    # ===== Итераторы =====

    def iterate_series(self, **query: Any) -> Iterator[Series]:
        """Проходит все аниме через afterId (рекомендуемый API способ полного сканирования)."""
        query.pop("offset", None)
        query.pop("after_id", None)
        query.pop("order", None)
        limit = query.pop("limit", 200)
        after_id: int | None = None
        while True:
            page = self.get_series(**query, limit=limit, order="id", after_id=after_id)
            if not page:
                return
            yield from page
            after_id = page[-1].id

    def iterate_episodes(self, **query: Any) -> Iterator[Episode]:
        """Проходит все эпизоды через afterId."""
        query.pop("offset", None)
        query.pop("after_id", None)
        limit = query.pop("limit", 200)
        after_id: int | None = None
        while True:
            page = self.get_episodes(**query, limit=limit, after_id=after_id)
            if not page:
                return
            yield from page
            after_id = page[-1].id

    def iterate_translations(self, **query: Any) -> Iterator[Translation]:
        """Проходит все переводы через afterId. По умолчанию feed="all" (включая неактивные)."""
        query.pop("offset", None)
        query.pop("after_id", None)
        limit = query.pop("limit", 200)
        feed = query.pop("feed", "all")
        after_id: int | None = None
        while True:
            page = self.get_translations(**query, limit=limit, feed=feed, after_id=after_id)
            if not page:
                return
            yield from page
            after_id = page[-1].id


class AsyncAnime365(_Anime365Base):
    """Асинхронный клиент API anime365 — та же поверхность, что и Anime365, на httpx.AsyncClient."""

    def __init__(self, *args: Any, client: httpx.AsyncClient | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client = client or httpx.AsyncClient(timeout=self.timeout)
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncAnime365:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    # ===== Транспорт =====

    async def request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        method: str = "GET",
        json: Any = None,
    ) -> Any:
        """Универсальный escape hatch для эндпоинтов, которых нет в типизированных методах ниже."""
        order = self._mirror_order()
        last_error: Anime365NetworkError | None = None
        failed_mirrors: list[str] = []

        for mirror in order:
            try:
                result = await self._request_with_retries(mirror, path, params, method=method, json=json)
                self._active_mirror_index = self._mirrors.index(mirror)
                return result
            except Anime365NetworkError as err:
                last_error = err
                failed_mirrors.append(mirror)
                continue

        raise Anime365NetworkError(
            f"Не удалось подключиться ни к одному из зеркал API ({', '.join(failed_mirrors)}): {last_error}"
        )

    async def _request_with_retries(
        self, mirror: str, path: str, params: dict[str, Any] | None, *, method: str, json: Any
    ) -> Any:
        last_error: Anime365NetworkError | None = None
        for attempt in range(self.retries + 1):
            if attempt > 0:
                await asyncio.sleep(retry_delay(attempt - 1, self.retry_delay_base))
            try:
                return await self._request_once(mirror, path, params, method=method, json=json)
            except Anime365NetworkError as err:
                last_error = err
                continue
        assert last_error is not None
        raise last_error

    async def _request_once(
        self, mirror: str, path: str, params: dict[str, Any] | None, *, method: str, json: Any
    ) -> Any:
        url = f"{mirror}{path}"
        query = self._build_params(mirror, params)
        try:
            response = await self._client.request(method, url, params=query, headers=self._headers(), json=json)
        except httpx.HTTPError as cause:
            raise Anime365NetworkError(f"Не удалось выполнить запрос к {url}: {cause}") from cause

        if response.status_code >= 500:
            raise Anime365NetworkError(f"Сервер {mirror} ответил {response.status_code} {response.reason_phrase}")

        try:
            payload = response.json()
        except ValueError as cause:
            raise Anime365NetworkError(
                f"Не удалось разобрать ответ API ({response.status_code} {response.reason_phrase})"
            ) from cause

        return parse_payload(payload)

    # ===== Аккаунт =====

    async def login(self, email: str, password: str) -> str:
        data = await self.request("/login", {"app": self.app, "email": email, "password": password})
        token = AccessTokenResponse.model_validate(data).access_token
        self.access_token = token
        return token

    async def fetch_access_token(self) -> str:
        data = await self.request("/accessToken", {"app": self.app})
        token = AccessTokenResponse.model_validate(data).access_token
        self.access_token = token
        return token

    async def get_me(self) -> User:
        return User.model_validate(await self.request("/me"))

    # ===== Каталог =====

    async def get_series(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        query: str | None = None,
        chips: ChipsParam = None,
        after_id: int | None = None,
        order: Literal["id"] | None = None,
        my_anime_list_id: int | None = None,
        is_active: Literal[0, 1] | None = None,
        is_airing: Literal[0, 1] | None = None,
        type: str | None = None,
        year: int | None = None,
        season: str | None = None,
    ) -> list[Series]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "query": query,
            "chips": _resolve_chips(chips),
            "afterId": after_id,
            "order": order,
            "myAnimeListId": my_anime_list_id,
            "isActive": is_active,
            "isAiring": is_airing,
            "type": type,
            "year": year,
            "season": season,
        }
        return [Series.model_validate(item) for item in await self.request("/series", params)]

    async def get_series_by_id(self, series_id: int, *, fields: FieldsParam = None) -> Series:
        return Series.model_validate(await self.request(f"/series/{series_id}", {"fields": fields}))

    async def get_episodes(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        series_id: int | None = None,
        episode_int: float | str | None = None,
        episode_type: Literal["tv", "movie", "ova", "ona", "special"] | None = None,
        is_active: Literal[0, 1] | None = None,
        is_first_uploaded: Literal[0, 1] | None = None,
        after_id: int | None = None,
    ) -> list[Episode]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "seriesId": series_id,
            "episodeInt": episode_int,
            "episodeType": episode_type,
            "isActive": is_active,
            "isFirstUploaded": is_first_uploaded,
            "afterId": after_id,
        }
        return [Episode.model_validate(item) for item in await self.request("/episodes", params)]

    async def get_episode_by_id(self, episode_id: int, *, fields: FieldsParam = None) -> Episode:
        return Episode.model_validate(await self.request(f"/episodes/{episode_id}", {"fields": fields}))

    async def get_video_by_id(self, video_id: int) -> Video:
        return Video.model_validate(await self.request(f"/videos/{video_id}"))

    # ===== Переводы =====

    async def get_translations(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        fields: FieldsParam = None,
        series_id: int | None = None,
        episode_id: int | None = None,
        feed: Literal["recent", "id", "all", "updatedDateTime", "addedDateTime"] | None = None,
        after_id: int | None = None,
        type: str | None = None,
        quality_type: str | None = None,
        is_active: Literal[0, 1] | None = None,
    ) -> list[Translation]:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "seriesId": series_id,
            "episodeId": episode_id,
            "feed": feed,
            "afterId": after_id,
            "type": type,
            "qualityType": quality_type,
            "isActive": is_active,
        }
        return [Translation.model_validate(item) for item in await self.request("/translations", params)]

    async def get_translation_by_id(self, translation_id: int, *, fields: FieldsParam = None) -> Translation:
        return Translation.model_validate(await self.request(f"/translations/{translation_id}", {"fields": fields}))

    async def get_translation_embed(self, translation_id: int) -> EmbedTranslation:
        embed = EmbedTranslation.model_validate(await self.request(f"/translations/embed/{translation_id}"))
        if embed.subtitles_url:
            embed.subtitles_url = absolutize(self._site_url, embed.subtitles_url)
        return embed

    # ===== Загрузка видео =====

    async def get_upload_endpoints(self) -> UploadEndpoints:
        return UploadEndpoints.model_validate(await self.request("/upload/endpoints"))

    async def create_translation(self, payload: TranslationCreateRequest) -> Translation:
        body = payload.model_dump(by_alias=True, exclude_none=True)
        return Translation.model_validate(await self.request("/translations/create", method="POST", json=body))

    # ===== Итераторы =====

    async def iterate_series(self, **query: Any) -> AsyncIterator[Series]:
        query.pop("offset", None)
        query.pop("after_id", None)
        query.pop("order", None)
        limit = query.pop("limit", 200)
        after_id: int | None = None
        while True:
            page = await self.get_series(**query, limit=limit, order="id", after_id=after_id)
            if not page:
                return
            for item in page:
                yield item
            after_id = page[-1].id

    async def iterate_episodes(self, **query: Any) -> AsyncIterator[Episode]:
        query.pop("offset", None)
        query.pop("after_id", None)
        limit = query.pop("limit", 200)
        after_id: int | None = None
        while True:
            page = await self.get_episodes(**query, limit=limit, after_id=after_id)
            if not page:
                return
            for item in page:
                yield item
            after_id = page[-1].id

    async def iterate_translations(self, **query: Any) -> AsyncIterator[Translation]:
        query.pop("offset", None)
        query.pop("after_id", None)
        limit = query.pop("limit", 200)
        feed = query.pop("feed", "all")
        after_id: int | None = None
        while True:
            page = await self.get_translations(**query, limit=limit, feed=feed, after_id=after_id)
            if not page:
                return
            for item in page:
                yield item
            after_id = page[-1].id

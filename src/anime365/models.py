"""Pydantic-модели ответов API.

Поля объявлены в snake_case, но API отдаёт camelCase — за перевод отвечает
``alias_generator=to_camel``. ``populate_by_name=True`` позволяет также
собирать модели по snake_case-именам (удобно в тестах), а ``extra="allow"``
не даёт упасть, если API добавит новое поле.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

if TYPE_CHECKING:
    pass


class _Base(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="allow")


class Link(_Base):
    """Ссылка на внешний ресурс (World Art, AniDB и т.д.) в карточке аниме."""

    title: str
    url: str


class Description(_Base):
    """Описание аниме от одного источника (Shikimori и т.д.)."""

    source: str
    value: str
    updated_date_time: str | None = None


class Titles(_Base):
    """Названия аниме по языкам."""

    romaji: str | None = None
    ru: str | None = None
    en: str | None = None
    ja: str | None = None


class Genre(_Base):
    id: int
    title: str
    url: str


class Episode(_Base):
    """Эпизод аниме."""

    id: int
    series_id: int
    episode_full: str
    episode_int: str
    """Номер серии — приходит строкой, в т.ч. отрицательной ("-6" для трейлеров/спецматериалов)."""
    episode_title: str
    episode_type: str
    first_uploaded_date_time: str
    is_active: int
    is_first_uploaded: int
    translations: list[Translation] | None = None


class Series(_Base):
    """Аниме (сериал/фильм). Состав полей зависит от параметра ``fields``."""

    id: int
    ani_db_id: int | None = None
    anime_news_network_id: int | None = None
    fansubs_id: int | None = None
    imdb_id: int | None = None
    world_art_id: int | None = None
    is_active: int
    is_airing: int
    is_hentai: int
    links: list[Link] | None = None
    my_anime_list_id: int | None = None
    anilist_id: int | None = None
    my_anime_list_score: str | None = None
    world_art_score: str | None = None
    world_art_top_place: str | int | None = None
    number_of_episodes: int | None = None
    season: str | None = None
    year: int | None = None
    type: str | None = None
    type_title: str | None = None
    titles: Titles | None = None
    poster_url: str | None = None
    poster_url_small: str | None = None
    title_lines: list[str] | None = None
    all_titles: list[str] | None = None
    title: str | None = None
    url: str | None = None
    descriptions: list[Description] | None = None
    episodes: list[Episode] | None = None
    genres: list[Genre] | None = None


class Translation(_Base):
    """Перевод (озвучка или субтитры) одного эпизода."""

    id: int
    series_id: int
    episode_id: int
    added_date_time: str
    active_date_time: str
    updated_date_time: str
    authors_list: list[str] | None = None
    authors_summary: str | None = None
    fansubs_translation_id: int | None = None
    is_active: int
    priority: int | None = None
    quality_type: str | None = None
    type: str
    """Например voiceRu, subRu, voiceEn, subEn, raw."""
    type_kind: str | None = None
    type_lang: str | None = None
    title: str | None = None
    url: str | None = None
    embed_url: str | None = None
    duration: str | None = None
    width: int | None = None
    height: int | None = None
    episode: Episode | None = None
    series: Series | None = None


class Video(_Base):
    """Отдельный видеофайл перевода (эндпоинт /videos/{id})."""

    id: int
    episode_id: int
    series_id: int
    filename: str
    type: str
    type_kind: str | None = None
    type_lang: str | None = None
    url_list: list[str] = Field(default_factory=list)


class DownloadOption(_Base):
    height: int
    url: str


class StreamOption(_Base):
    height: int
    urls: list[str] = Field(default_factory=list)


class EmbedTranslation(_Base):
    """Ссылки на видео/субтитры для воспроизведения — требует access_token с активной подпиской."""

    embed_url: str | None = None
    download: list[DownloadOption] = Field(default_factory=list)
    stream: list[StreamOption] = Field(default_factory=list)
    subtitles_url: str | None = None
    """В сыром ответе API бывает относительным; клиент приводит к абсолютному URL."""
    subtitles_vtt_url: str | None = None


class User(_Base):
    is_logined: bool
    id: int | None = None
    name: str | None = None
    is_premium: bool | None = None
    premium_until: str | None = None


class AccessTokenResponse(_Base):
    access_token: str = Field(alias="access_token")


class UploadEndpoint(_Base):
    """Один канал загрузки видео (tus) из /upload/endpoints."""

    id: str
    label: str
    server_id: int
    tus_url: str
    tus_urls: list[str] = Field(default_factory=list)
    recommended: bool = False


class UploadEndpoints(_Base):
    recommended_id: str
    endpoints: list[UploadEndpoint] = Field(default_factory=list)


class TranslationCreateRequest(_Base):
    """Тело запроса POST /translations/create."""

    series_id: int
    episode_number: float
    episode_type: str
    """tv, movie, ova, ona, special и т.д."""
    type: str
    """voiceRu, subRu, voiceEn, subEn, raw и т.д."""
    authors: str | None = None
    added_by_author: Literal[0, 1] | None = None
    """1, если вы участник команды авторов этого перевода."""
    server_id: int
    """ID сервера загрузки (X-Upload-Server-Id из ответа tus)."""
    video_uuid: str
    video_filename: str
    video_size: int
    video_sha256: str | None = None
    sub_uuid: str | None = None
    sub_filename: str | None = None
    sub_size: int | None = None
    sub_sha256: str | None = None


Episode.model_rebuild()
Series.model_rebuild()
Translation.model_rebuild()

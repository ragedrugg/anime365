"""Клиент API anime365 (smotret-anime.app / anime365.ru): каталог, переводы, видео, аккаунт, загрузка."""

from ._core import DEFAULT_MIRRORS
from .chips import Chip, ChipCondition, build_chips
from .client import Anime365, AsyncAnime365
from .errors import Anime365Error, Anime365NetworkError
from .models import (
    AccessTokenResponse,
    Description,
    DownloadOption,
    EmbedTranslation,
    Episode,
    Genre,
    Link,
    Series,
    StreamOption,
    Titles,
    Translation,
    TranslationCreateRequest,
    UploadEndpoint,
    UploadEndpoints,
    User,
    Video,
)
from .upload import (
    FileSource,
    TusUploadResult,
    add_translation,
    add_translation_async,
    bytes_source,
    file_source,
)

__version__ = "2.0.0"

__all__ = [
    "AccessTokenResponse",
    "Anime365",
    "Anime365Error",
    "Anime365NetworkError",
    "AsyncAnime365",
    "Chip",
    "ChipCondition",
    "DEFAULT_MIRRORS",
    "Description",
    "DownloadOption",
    "EmbedTranslation",
    "Episode",
    "FileSource",
    "Genre",
    "Link",
    "Series",
    "StreamOption",
    "Titles",
    "Translation",
    "TranslationCreateRequest",
    "TusUploadResult",
    "UploadEndpoint",
    "UploadEndpoints",
    "User",
    "Video",
    "__version__",
    "add_translation",
    "add_translation_async",
    "build_chips",
    "bytes_source",
    "file_source",
]

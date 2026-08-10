"""Загрузка видео по протоколу tus 1.0.0 и добавление перевода.

Порт `src/upload.ts` из TS-версии: `POST` создаёт загрузку, `PATCH` шлёт
чанки с `Upload-Offset`, `HEAD` позволяет узнать смещение для докачки после
обрыва связи.
"""

from __future__ import annotations

import base64
import hashlib
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol

import anyio
import httpx

from .models import Translation, TranslationCreateRequest, UploadEndpoint

if TYPE_CHECKING:
    from .client import Anime365, AsyncAnime365

DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024

_LOCATION_ID_RE = re.compile(r"[?&]id=([^&]+)")


class FileSource(Protocol):
    """Абстракция над источником данных для tus-загрузки: файл или буфер в памяти."""

    filename: str
    size: int

    def read(self, offset: int, length: int) -> bytes: ...


@dataclass
class _PathFileSource:
    path: Path
    filename: str
    size: int

    def read(self, offset: int, length: int) -> bytes:
        with self.path.open("rb") as fh:
            fh.seek(offset)
            return fh.read(length)


@dataclass
class _BytesFileSource:
    data: bytes
    filename: str
    size: int = field(init=False)

    def __post_init__(self) -> None:
        self.size = len(self.data)

    def read(self, offset: int, length: int) -> bytes:
        return self.data[offset : offset + length]


def file_source(path: str | Path, filename: str | None = None) -> FileSource:
    """Источник из файла на диске, читается по смещению без загрузки целиком в память."""
    p = Path(path)
    return _PathFileSource(path=p, filename=filename or p.name, size=p.stat().st_size)


def bytes_source(data: bytes, filename: str = "upload.bin") -> FileSource:
    """Источник из буфера в памяти (например, скачанного заранее файла)."""
    return _BytesFileSource(data=data, filename=filename)


def _sha256_of_source(source: FileSource, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    digest = hashlib.sha256()
    offset = 0
    while offset < source.size:
        digest.update(source.read(offset, min(chunk_size, source.size - offset)))
        offset += chunk_size
    return digest.hexdigest()


@dataclass
class TusUploadResult:
    uuid: str
    server_id: int | None = None


def _upload_metadata_header(filename: str) -> str:
    return f"filename {base64.b64encode(filename.encode()).decode()}"


def upload_to_channel(
    client: httpx.Client,
    channel: UploadEndpoint,
    source: FileSource,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    resume_uuid: str | None = None,
    on_progress: Callable[[int, int], None] | None = None,
) -> TusUploadResult:
    """Загружает `source` на один из `tus_urls` канала (синхронно)."""
    last_error: Exception | None = None
    for tus_url in channel.tus_urls or [channel.tus_url]:
        try:
            return _upload_to_url(
                client, tus_url, source, chunk_size=chunk_size, resume_uuid=resume_uuid, on_progress=on_progress
            )
        except httpx.HTTPError as err:
            last_error = err
            continue
    raise RuntimeError(f"tus: не удалось загрузить ни на один эндпоинт канала {channel.id}") from last_error


def _upload_to_url(
    client: httpx.Client,
    tus_url: str,
    source: FileSource,
    *,
    chunk_size: int,
    resume_uuid: str | None,
    on_progress: Callable[[int, int], None] | None,
) -> TusUploadResult:
    if resume_uuid:
        uuid = resume_uuid
        head_res = client.head(f"{tus_url}?id={uuid}", headers={"Tus-Resumable": "1.0.0"})
        if head_res.is_error:
            raise RuntimeError(f"tus: не удалось узнать смещение для докачки {uuid} ({head_res.status_code})")
        offset = int(head_res.headers.get("Upload-Offset", 0))
    else:
        create_res = client.post(
            tus_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(source.size),
                "Upload-Metadata": _upload_metadata_header(source.filename),
            },
        )
        if create_res.is_error:
            raise RuntimeError(f"tus: не удалось создать загрузку на {tus_url} ({create_res.status_code})")
        uuid = _extract_uuid(create_res)
        offset = 0

    patch_url = f"{tus_url}?id={uuid}"
    while offset < source.size:
        length = min(chunk_size, source.size - offset)
        chunk = source.read(offset, length)
        patch_res = client.patch(
            patch_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": str(offset),
            },
            content=chunk,
        )
        if patch_res.is_error:
            raise RuntimeError(f"tus: сбой загрузки чанка ({patch_res.status_code})")
        offset = int(patch_res.headers.get("Upload-Offset", offset + length))
        if on_progress:
            on_progress(offset, source.size)

    return TusUploadResult(uuid=uuid)


def _extract_uuid(response: httpx.Response) -> str:
    header_uuid = response.headers.get("X-Upload-Uuid")
    if header_uuid:
        return str(header_uuid)
    location = response.headers.get("Location")
    match = _LOCATION_ID_RE.search(location) if location else None
    if match:
        return str(match.group(1))
    raise RuntimeError("tus: сервер не вернул ни X-Upload-Uuid, ни Location с id")


async def upload_to_channel_async(
    client: httpx.AsyncClient,
    channel: UploadEndpoint,
    source: FileSource,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    resume_uuid: str | None = None,
    on_progress: Callable[[int, int], Awaitable[None] | None] | None = None,
) -> TusUploadResult:
    """Загружает `source` на один из `tus_urls` канала (асинхронно, чтение файла в потоке)."""
    last_error: Exception | None = None
    for tus_url in channel.tus_urls or [channel.tus_url]:
        try:
            return await _upload_to_url_async(
                client, tus_url, source, chunk_size=chunk_size, resume_uuid=resume_uuid, on_progress=on_progress
            )
        except httpx.HTTPError as err:
            last_error = err
            continue
    raise RuntimeError(f"tus: не удалось загрузить ни на один эндпоинт канала {channel.id}") from last_error


async def _upload_to_url_async(
    client: httpx.AsyncClient,
    tus_url: str,
    source: FileSource,
    *,
    chunk_size: int,
    resume_uuid: str | None,
    on_progress: Callable[[int, int], Awaitable[None] | None] | None,
) -> TusUploadResult:
    if resume_uuid:
        uuid = resume_uuid
        head_res = await client.head(f"{tus_url}?id={uuid}", headers={"Tus-Resumable": "1.0.0"})
        if head_res.is_error:
            raise RuntimeError(f"tus: не удалось узнать смещение для докачки {uuid} ({head_res.status_code})")
        offset = int(head_res.headers.get("Upload-Offset", 0))
    else:
        create_res = await client.post(
            tus_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(source.size),
                "Upload-Metadata": _upload_metadata_header(source.filename),
            },
        )
        if create_res.is_error:
            raise RuntimeError(f"tus: не удалось создать загрузку на {tus_url} ({create_res.status_code})")
        uuid = _extract_uuid(create_res)
        offset = 0

    patch_url = f"{tus_url}?id={uuid}"
    while offset < source.size:
        length = min(chunk_size, source.size - offset)
        chunk = await anyio.to_thread.run_sync(source.read, offset, length)
        patch_res = await client.patch(
            patch_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": str(offset),
            },
            content=chunk,
        )
        if patch_res.is_error:
            raise RuntimeError(f"tus: сбой загрузки чанка ({patch_res.status_code})")
        offset = int(patch_res.headers.get("Upload-Offset", offset + length))
        if on_progress:
            result = on_progress(offset, source.size)
            if result is not None:
                await result

    return TusUploadResult(uuid=uuid)


def add_translation(
    client: Anime365,
    *,
    series_id: int,
    episode_number: float,
    episode_type: str,
    type: str,
    video: FileSource,
    subtitles: FileSource | None = None,
    authors: str | None = None,
    added_by_author: Literal[0, 1] | None = None,
    channel_id: str | None = None,
    compute_sha256: bool = False,
    on_video_progress: Callable[[int, int], None] | None = None,
    on_subtitles_progress: Callable[[int, int], None] | None = None,
) -> Translation:
    """Полный флоу: получает точки загрузки, заливает видео (и субтитры) по tus, создаёт перевод."""
    endpoints = client.get_upload_endpoints()
    wanted_id = channel_id or endpoints.recommended_id
    channel = next((e for e in endpoints.endpoints if e.id == wanted_id), None) or endpoints.endpoints[0]

    video_result = upload_to_channel(client._client, channel, video, on_progress=on_video_progress)
    video_sha256 = _sha256_of_source(video) if compute_sha256 else None

    sub_uuid: str | None = None
    sub_sha256: str | None = None
    if subtitles is not None:
        sub_result = upload_to_channel(client._client, channel, subtitles, on_progress=on_subtitles_progress)
        sub_uuid = sub_result.uuid
        sub_sha256 = _sha256_of_source(subtitles) if compute_sha256 else None

    payload = TranslationCreateRequest(
        series_id=series_id,
        episode_number=episode_number,
        episode_type=episode_type,
        type=type,
        authors=authors,
        added_by_author=added_by_author,
        server_id=channel.server_id,
        video_uuid=video_result.uuid,
        video_filename=video.filename,
        video_size=video.size,
        video_sha256=video_sha256,
        sub_uuid=sub_uuid,
        sub_filename=subtitles.filename if subtitles else None,
        sub_size=subtitles.size if subtitles else None,
        sub_sha256=sub_sha256,
    )
    return client.create_translation(payload)


async def add_translation_async(
    client: AsyncAnime365,
    *,
    series_id: int,
    episode_number: float,
    episode_type: str,
    type: str,
    video: FileSource,
    subtitles: FileSource | None = None,
    authors: str | None = None,
    added_by_author: Literal[0, 1] | None = None,
    channel_id: str | None = None,
    compute_sha256: bool = False,
    on_video_progress: Callable[[int, int], Awaitable[None] | None] | None = None,
    on_subtitles_progress: Callable[[int, int], Awaitable[None] | None] | None = None,
) -> Translation:
    """Асинхронный вариант add_translation."""
    endpoints = await client.get_upload_endpoints()
    wanted_id = channel_id or endpoints.recommended_id
    channel = next((e for e in endpoints.endpoints if e.id == wanted_id), None) or endpoints.endpoints[0]

    video_result = await upload_to_channel_async(client._client, channel, video, on_progress=on_video_progress)
    video_sha256 = await anyio.to_thread.run_sync(_sha256_of_source, video) if compute_sha256 else None

    sub_uuid: str | None = None
    sub_sha256: str | None = None
    if subtitles is not None:
        sub_result = await upload_to_channel_async(
            client._client, channel, subtitles, on_progress=on_subtitles_progress
        )
        sub_uuid = sub_result.uuid
        sub_sha256 = await anyio.to_thread.run_sync(_sha256_of_source, subtitles) if compute_sha256 else None

    payload = TranslationCreateRequest(
        series_id=series_id,
        episode_number=episode_number,
        episode_type=episode_type,
        type=type,
        authors=authors,
        added_by_author=added_by_author,
        server_id=channel.server_id,
        video_uuid=video_result.uuid,
        video_filename=video.filename,
        video_size=video.size,
        video_sha256=video_sha256,
        sub_uuid=sub_uuid,
        sub_filename=subtitles.filename if subtitles else None,
        sub_size=subtitles.size if subtitles else None,
        sub_sha256=sub_sha256,
    )
    return await client.create_translation(payload)

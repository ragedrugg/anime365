import httpx
import pytest
import respx

from anime365.models import UploadEndpoint
from anime365.upload import bytes_source, upload_to_channel, upload_to_channel_async

TUS_URL = "https://time28.anime-on.ru/tus.php"

CHANNEL = UploadEndpoint(
    id="2", label="CDN", server_id=28, tus_url=TUS_URL, tus_urls=[TUS_URL], recommended=True
)


@respx.mock
def test_upload_to_channel_creates_then_patches_in_chunks() -> None:
    source = bytes_source(b"0123456789", filename="episode.mp4")

    respx.post(TUS_URL).mock(
        return_value=httpx.Response(201, headers={"X-Upload-Uuid": "uuid-1"})
    )
    respx.patch(TUS_URL).mock(
        side_effect=[
            httpx.Response(204, headers={"Upload-Offset": "5"}),
            httpx.Response(204, headers={"Upload-Offset": "10"}),
        ]
    )

    with httpx.Client() as client:
        result = upload_to_channel(client, CHANNEL, source, chunk_size=5)

    assert result.uuid == "uuid-1"
    patch_calls = [c for c in respx.calls if c.request.method == "PATCH"]
    assert len(patch_calls) == 2
    assert patch_calls[0].request.headers["Upload-Offset"] == "0"
    assert patch_calls[1].request.headers["Upload-Offset"] == "5"


@respx.mock
def test_upload_to_channel_resumes_via_head() -> None:
    source = bytes_source(b"0123456789", filename="episode.mp4")

    respx.head(f"{TUS_URL}?id=uuid-1").mock(
        return_value=httpx.Response(200, headers={"Upload-Offset": "7"})
    )
    respx.patch(TUS_URL).mock(return_value=httpx.Response(204, headers={"Upload-Offset": "10"}))

    with httpx.Client() as client:
        result = upload_to_channel(client, CHANNEL, source, resume_uuid="uuid-1")

    assert result.uuid == "uuid-1"
    patch_calls = [c for c in respx.calls if c.request.method == "PATCH"]
    assert len(patch_calls) == 1
    assert patch_calls[0].request.headers["Upload-Offset"] == "7"


@respx.mock
@pytest.mark.asyncio
async def test_upload_to_channel_async_creates_then_patches() -> None:
    source = bytes_source(b"0123456789", filename="episode.mp4")

    respx.post(TUS_URL).mock(return_value=httpx.Response(201, headers={"X-Upload-Uuid": "uuid-2"}))
    respx.patch(TUS_URL).mock(return_value=httpx.Response(204, headers={"Upload-Offset": "10"}))

    async with httpx.AsyncClient() as client:
        result = await upload_to_channel_async(client, CHANNEL, source)

    assert result.uuid == "uuid-2"

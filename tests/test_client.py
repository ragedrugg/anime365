import httpx
import pytest
import respx

from anime365 import Anime365, Anime365Error, Anime365NetworkError, AsyncAnime365

M1 = "https://mirror1.test/api"
M2 = "https://mirror2.test/api"


@respx.mock
def test_get_series_parses_response() -> None:
    respx.get(f"{M1}/series").mock(
        return_value=httpx.Response(200, json={"data": [{"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0}]})
    )
    client = Anime365(base_url=M1)
    series = client.get_series(query="naruto")
    assert len(series) == 1
    assert series[0].id == 1
    request = respx.calls.last.request
    assert request.url.params["query"] == "naruto"


@respx.mock
def test_api_error_does_not_retry() -> None:
    route = respx.get(f"{M1}/translations/embed/1").mock(
        return_value=httpx.Response(200, json={"error": {"code": 403, "message": "Authorization required."}})
    )
    client = Anime365(base_url=M1)
    with pytest.raises(Anime365Error) as exc_info:
        client.get_translation_embed(1)
    assert exc_info.value.code == 403
    assert route.call_count == 1


@respx.mock
def test_network_error_fails_over_to_next_mirror() -> None:
    respx.get(f"{M1}/series/1").mock(side_effect=httpx.ConnectError("boom"))
    respx.get(f"{M2}/series/1").mock(
        return_value=httpx.Response(200, json={"data": {"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0}})
    )
    client = Anime365(base_url=[M1, M2], retries=0, retry_delay_base=0.001)
    series = client.get_series_by_id(1)
    assert series.id == 1
    assert client.active_base_url == M2


@respx.mock
def test_server_error_retries_then_raises() -> None:
    route = respx.get(f"{M1}/series/1").mock(return_value=httpx.Response(500))
    client = Anime365(base_url=M1, retries=2, retry_delay_base=0.001)
    with pytest.raises(Anime365NetworkError):
        client.get_series_by_id(1)
    assert route.call_count == 3


@respx.mock
def test_login_stores_access_token() -> None:
    respx.get(f"{M1}/login").mock(return_value=httpx.Response(200, json={"data": {"access_token": "tok123"}}))
    client = Anime365(base_url=M1)
    token = client.login("user@example.com", "hunter2")
    assert token == "tok123"
    assert client.access_token == "tok123"


@respx.mock
def test_embed_absolutizes_subtitles_url() -> None:
    respx.get(f"{M1}/translations/embed/1").mock(
        return_value=httpx.Response(200, json={"data": {"subtitlesUrl": "/subs/1.ass"}})
    )
    client = Anime365(base_url=M1)
    embed = client.get_translation_embed(1)
    assert embed.subtitles_url == "https://mirror1.test/subs/1.ass"


@respx.mock
def test_iterate_series_paginates_via_after_id() -> None:
    respx.get(f"{M1}/series").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "data": [
                        {"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0},
                        {"id": 2, "isActive": 1, "isAiring": 0, "isHentai": 0},
                    ]
                },
            ),
            httpx.Response(200, json={"data": []}),
        ]
    )
    client = Anime365(base_url=M1)
    items = list(client.iterate_series(limit=2))
    assert [item.id for item in items] == [1, 2]


@respx.mock
@pytest.mark.asyncio
async def test_async_get_series_parses_response() -> None:
    respx.get(f"{M1}/series").mock(
        return_value=httpx.Response(200, json={"data": [{"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0}]})
    )
    async with AsyncAnime365(base_url=M1) as client:
        series = await client.get_series()
    assert series[0].id == 1


@respx.mock
@pytest.mark.asyncio
async def test_async_network_error_fails_over_to_next_mirror() -> None:
    respx.get(f"{M1}/series/1").mock(side_effect=httpx.ConnectError("boom"))
    respx.get(f"{M2}/series/1").mock(
        return_value=httpx.Response(200, json={"data": {"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0}})
    )
    async with AsyncAnime365(base_url=[M1, M2], retries=0, retry_delay_base=0.001) as client:
        series = await client.get_series_by_id(1)
    assert series.id == 1


@respx.mock
@pytest.mark.asyncio
async def test_async_iterate_translations_paginates() -> None:
    respx.get(f"{M1}/translations").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": 10,
                            "seriesId": 1,
                            "episodeId": 1,
                            "addedDateTime": "",
                            "activeDateTime": "",
                            "updatedDateTime": "",
                            "isActive": 1,
                            "type": "voiceRu",
                        }
                    ]
                },
            ),
            httpx.Response(200, json={"data": []}),
        ]
    )
    async with AsyncAnime365(base_url=M1) as client:
        items = [item async for item in client.iterate_translations(limit=1)]
    assert [item.id for item in items] == [10]

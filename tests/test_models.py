from anime365.models import AccessTokenResponse, Episode, Series, Translation, UploadEndpoints, User


def test_series_parses_raw_camel_case() -> None:
    series = Series.model_validate(
        {
            "id": 8245,
            "isActive": 1,
            "isAiring": 0,
            "isHentai": 0,
            "myAnimeListId": 12345,
            "myAnimeListScore": "8.12",
            "worldArtScore": "7.5",
            "worldArtTopPlace": None,
            "posterUrlSmall": "https://smotret-anime.app/poster.jpg",
            "titles": {"ru": "Тест", "en": "Test"},
        }
    )
    assert series.id == 8245
    assert series.my_anime_list_score == "8.12"
    assert series.world_art_top_place is None
    assert series.poster_url_small == "https://smotret-anime.app/poster.jpg"
    assert series.titles is not None
    assert series.titles.ru == "Тест"


def test_series_allows_unknown_fields() -> None:
    series = Series.model_validate({"id": 1, "isActive": 1, "isAiring": 0, "isHentai": 0, "somethingNew": "value"})
    assert series.id == 1


def test_episode_int_is_string() -> None:
    episode = Episode.model_validate(
        {
            "id": 1,
            "seriesId": 8245,
            "episodeFull": "-6",
            "episodeInt": "-6",
            "episodeTitle": "",
            "episodeType": "special",
            "firstUploadedDateTime": "2024-01-01 00:00:00",
            "isActive": 1,
            "isFirstUploaded": 0,
        }
    )
    assert episode.episode_int == "-6"
    assert isinstance(episode.episode_int, str)


def test_translation_by_alias_round_trips() -> None:
    translation = Translation.model_validate(
        {
            "id": 1,
            "seriesId": 2,
            "episodeId": 3,
            "addedDateTime": "",
            "activeDateTime": "",
            "updatedDateTime": "",
            "isActive": 1,
            "type": "voiceRu",
        }
    )
    dumped = translation.model_dump(by_alias=True)
    assert dumped["seriesId"] == 2
    assert dumped["episodeId"] == 3


def test_access_token_response_uses_snake_case_alias() -> None:
    resp = AccessTokenResponse.model_validate({"access_token": "abc123"})
    assert resp.access_token == "abc123"


def test_user_guest() -> None:
    user = User.model_validate({"isLogined": False})
    assert user.is_logined is False
    assert user.id is None


def test_upload_endpoints_parses_channels() -> None:
    endpoints = UploadEndpoints.model_validate(
        {
            "recommendedId": "2",
            "endpoints": [
                {
                    "id": "2",
                    "label": "CDN",
                    "serverId": 28,
                    "tusUrl": "https://time28.anime-on.ru/tus.php",
                    "tusUrls": ["https://time28.anime-on.ru/tus.php"],
                    "recommended": True,
                }
            ],
        }
    )
    assert endpoints.recommended_id == "2"
    assert endpoints.endpoints[0].server_id == 28

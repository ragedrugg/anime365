import pytest

from anime365._core import absolutize, build_params, parse_payload, retry_delay
from anime365.errors import Anime365Error


def test_build_params_skips_none() -> None:
    assert build_params(a=1, b=None, c="x") == {"a": "1", "c": "x"}


def test_build_params_joins_lists() -> None:
    assert build_params(fields=["id", "title"]) == {"fields": "id,title"}


def test_build_params_bools() -> None:
    assert build_params(flag=True, other=False) == {"flag": "1", "other": "0"}


def test_parse_payload_returns_data() -> None:
    assert parse_payload({"data": {"id": 1}}) == {"id": 1}


def test_parse_payload_raises_on_error() -> None:
    with pytest.raises(Anime365Error) as exc_info:
        parse_payload({"error": {"code": 403, "message": "Authorization required."}})
    assert exc_info.value.code == 403
    assert exc_info.value.message == "Authorization required."


def test_parse_payload_carries_fields() -> None:
    with pytest.raises(Anime365Error) as exc_info:
        parse_payload({"error": {"code": 400, "message": "Validation error", "fields": {"type": ["required"]}}})
    assert exc_info.value.fields == {"type": ["required"]}


def test_retry_delay_grows_and_has_jitter() -> None:
    assert 0.15 <= retry_delay(0, 0.3) <= 0.3
    assert 0.3 <= retry_delay(1, 0.3) <= 0.6


def test_absolutize_leaves_absolute_urls() -> None:
    assert absolutize("https://smotret-anime.app", "https://cdn.example/x.vtt") == "https://cdn.example/x.vtt"


def test_absolutize_resolves_relative_urls() -> None:
    assert absolutize("https://smotret-anime.app", "/subs/1.ass") == "https://smotret-anime.app/subs/1.ass"

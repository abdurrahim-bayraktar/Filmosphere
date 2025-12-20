from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional

import pytest
from django.utils import timezone

from core.services import IMDbService, KinoCheckService, WatchmodeService
from films.models import Film
from films.services import FilmAggregatorService, FilmCacheService


class DummyHttpClient:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self.payload = payload
        self.calls: List[Dict[str, Any]] = []

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        self.calls.append({"url": url, "params": params, "headers": headers})
        return self.payload


@pytest.mark.django_db
def test_imdb_service_search_uses_http_client() -> None:
    client = DummyHttpClient({"results": [{"imdb_id": "tt1", "title": "Test"}]})
    service = IMDbService(http_client=client)

    results = service.search("Test")

    assert results[0]["imdb_id"] == "tt1"
    assert client.calls[0]["url"] == "/search"


@pytest.mark.django_db
def test_kinocheck_service_trailer_optional() -> None:
    client = DummyHttpClient({"id": "tr1"})
    service = KinoCheckService(http_client=client)

    trailer = service.get_trailer("tt1")

    assert trailer == {"id": "tr1"}


@pytest.mark.django_db
def test_watchmode_lookup_and_sources() -> None:
    client = DummyHttpClient({"title_results": [{"id": 42}]})
    service = WatchmodeService(http_client=client)

    watchmode_id = service.lookup_title_id("tt1")
    assert watchmode_id == 42


@pytest.mark.django_db
def test_film_cache_save_and_get(settings) -> None:
    settings.CACHE_TTL_HOURS = 24
    cache = FilmCacheService()
    payload = {"imdb_id": "tt1", "title": "Film", "metadata": {"year": 2010, "poster_url": "http://example.com"}}

    cache.save_cache("tt1", payload)

    cached = cache.get_cached("tt1")
    assert cached is not None
    assert cached["title"] == "Film"


@pytest.mark.django_db
def test_film_cache_is_fresh(settings) -> None:
    settings.CACHE_TTL_HOURS = 24
    film = Film.objects.create(
        imdb_id="tt1",
        title="Film",
        cached_at=timezone.now() - timedelta(hours=1),
    )
    cache = FilmCacheService()

    assert cache.is_fresh(film.imdb_id) is True


@pytest.mark.django_db
def test_aggregator_cache_hit_uses_cached_payload(settings) -> None:
    settings.CACHE_TTL_HOURS = 24
    payload = {
        "imdb_id": "tt1",
        "title": "Film",
        "metadata": {},
        "credits": {},
        "images": {},
        "videos": {},
        "parents_guide": {},
        "certificates": {},
        "release_dates": {},
        "trailer": None,
        "streaming": [],
        "warnings": [],
    }
    Film.objects.create(imdb_id="tt1", title="Film", cached_at=timezone.now(), full_json=payload)
    cache = FilmCacheService()

    class NoopService:
        def __getattr__(self, name: str) -> Any:
            raise AssertionError("External service should not be called on cache hit")

    aggregator = FilmAggregatorService(
        imdb_service=NoopService(),
        kino_service=NoopService(),
        watchmode_service=NoopService(),
        cache_service=cache,
    )

    result = aggregator.fetch_and_cache("tt1")

    assert result["imdb_id"] == "tt1"
    assert result["title"] == "Film"



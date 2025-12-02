from __future__ import annotations

from typing import Any, Dict, List

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

import films.views as film_views


class DummyIMDbService:
    def __init__(self) -> None:
        self.queries: List[str] = []

    def search(self, query: str) -> List[Dict[str, Any]]:
        self.queries.append(query)
        return [
            {"imdb_id": "tt1", "title": "Film", "year": 2010, "image": "img", "type": "movie"},
        ]


class DummyAggregator:
    def __init__(self) -> None:
        self.requested_ids: List[str] = []

    def fetch_and_cache(self, imdb_id: str) -> Dict[str, Any]:
        self.requested_ids.append(imdb_id)
        return {
            "imdb_id": imdb_id,
            "title": "Film",
            "metadata": {},
            "credits": {},
            "images": {},
            "videos": {},
            "parents_guide": {},
            "certificates": {},
            "release_dates": {},
            "trailer": {"id": "tr1"},
            "streaming": [{"source": "test"}],
            "warnings": [],
        }


@pytest.mark.django_db
def test_search_view_returns_results(monkeypatch) -> None:
    monkeypatch.setattr(film_views, "IMDbService", DummyIMDbService)
    client = APIClient()

    response = client.get("/api/search", {"q": "Inception"})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "Inception"
    assert len(body["results"]) == 1
    assert body["results"][0]["imdb_id"] == "tt1"


@pytest.mark.django_db
def test_search_view_requires_query_param() -> None:
    client = APIClient()
    response = client.get("/api/search")
    assert response.status_code == 400


@pytest.mark.django_db
def test_film_detail_view_uses_aggregator(monkeypatch) -> None:
    dummy_aggregator = DummyAggregator()

    class DummyAggregatorFactory:
        def __call__(self, *args: Any, **kwargs: Any) -> DummyAggregator:
            return dummy_aggregator

    monkeypatch.setattr(film_views, "FilmAggregatorService", DummyAggregatorFactory())
    client = APIClient()

    response = client.get("/api/films/tt1375666")

    assert response.status_code == 200
    body = response.json()
    assert body["imdb_id"] == "tt1375666"
    assert dummy_aggregator.requested_ids == ["tt1375666"]


@pytest.mark.django_db
def test_film_trailer_view(monkeypatch) -> None:
    dummy_aggregator = DummyAggregator()

    class DummyAggregatorFactory:
        def __call__(self, *args: Any, **kwargs: Any) -> DummyAggregator:
            return dummy_aggregator

    monkeypatch.setattr(film_views, "FilmAggregatorService", DummyAggregatorFactory())
    client = APIClient()

    response = client.get("/api/films/tt1375666/trailer")
    assert response.status_code == 200
    assert response.json()["trailer"] == {"id": "tr1"}


@pytest.mark.django_db
def test_film_streaming_view(monkeypatch) -> None:
    dummy_aggregator = DummyAggregator()

    class DummyAggregatorFactory:
        def __call__(self, *args: Any, **kwargs: Any) -> DummyAggregator:
            return dummy_aggregator

    monkeypatch.setattr(film_views, "FilmAggregatorService", DummyAggregatorFactory())
    client = APIClient()

    response = client.get("/api/films/tt1375666/streaming")
    assert response.status_code == 200
    assert response.json()["streaming"] == [{"source": "test"}]



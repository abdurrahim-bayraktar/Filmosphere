from __future__ import annotations

import re
from typing import Any, Dict

from django.http import Http404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import IMDbService
from films.serializers import SearchResultSerializer
from films.services import FilmAggregatorService

IMDB_ID_PATTERN = re.compile(r"^tt\d+$")


class SearchView(APIView):
    """Search films via IMDbService and return normalized results."""

    def __init__(self, imdb_service: IMDbService | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.imdb_service = imdb_service or IMDbService()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/search?q=<query>."""
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results_raw = self.imdb_service.search(query)
        serializer = SearchResultSerializer(results_raw, many=True)
        return Response({"query": query, "results": serializer.data})


class FilmDetailView(APIView):
    """Return full aggregated film payload for a given IMDb id."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload: Dict[str, Any] = self.aggregator.fetch_and_cache(imdb_id)
        return Response(payload)


class FilmTrailerView(APIView):
    """Return only trailer information for a film, using the aggregator output."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/trailer."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload = self.aggregator.fetch_and_cache(imdb_id)
        return Response({"imdb_id": imdb_id, "trailer": payload.get("trailer")})


class FilmStreamingView(APIView):
    """Return only streaming information for a film, using the aggregator output."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/streaming."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload = self.aggregator.fetch_and_cache(imdb_id)
        return Response({"imdb_id": imdb_id, "streaming": payload.get("streaming", [])})




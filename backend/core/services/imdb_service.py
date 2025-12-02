from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from django.conf import settings

from .http_client import HttpClient


class IMDbService:
    """Service wrapper for IMDbAPI.dev endpoints."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.IMDBAPI_BASE)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search films by text query using IMDbAPI `/search/titles`.

        This normalizes the external response into a simple list of
        {imdb_id, title, year, image, type} dictionaries suitable for the
        public search endpoint.
        """
        try:
            payload = self.http_client.get(
                "/search/titles",
                params={"query": query, "limit": 10},
            )
        except httpx.HTTPError:
            # Treat network / client errors as "no results" for now.
            return []
        titles = payload.get("titles", []) or []
        normalized: List[Dict[str, Any]] = []
        for item in titles:
            primary_image = item.get("primaryImage") or {}
            normalized.append(
                {
                    "imdb_id": item.get("id"),
                    "title": item.get("primaryTitle"),
                    "year": item.get("startYear"),
                    "image": primary_image.get("url"),
                    "type": item.get("type"),
                }
            )
        return normalized

    def get_metadata(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch core metadata for a film."""
        return self.http_client.get(f"/titles/{imdb_id}")

    def get_credits(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch credits information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/credits")

    def get_images(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch image gallery for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/images")

    def get_videos(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch related videos for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/videos")

    def get_parents_guide(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch parents guide information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/parentsGuide")

    def get_certificates(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch certification information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/certificates")

    def get_release_dates(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch release date information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/releaseDates")




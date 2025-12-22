from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.conf import settings

from .http_client import HttpClient


class WatchmodeService:
    """Service wrapper for Watchmode streaming API."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.WATCHMODE_BASE)

    def lookup_title_id(self, imdb_id: str) -> Optional[int]:
        """Look up the Watchmode title id for a given IMDb id."""
        params = {"imdb_id": imdb_id, "apiKey": settings.WATCHMODE_API_KEY}
        data = self.http_client.get("/search/", params=params)
        results = data.get("title_results") or []
        if not results:
            return None
        return results[0].get("id")

    def get_streaming_sources(self, watchmode_id: int) -> List[Dict[str, Any]]:
        """Retrieve streaming sources for the given Watchmode title id."""
        params = {"apiKey": settings.WATCHMODE_API_KEY, "regions": "TR"}
        data = self.http_client.get(f"/title/{watchmode_id}/sources/", params=params)
        return data or []




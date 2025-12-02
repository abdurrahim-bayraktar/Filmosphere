from __future__ import annotations

from typing import Any, Dict, Optional

from django.conf import settings

from .http_client import HttpClient


class KinoCheckService:
    """Service wrapper for KinoCheck trailer API."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.KINO_BASE)

    def get_trailer(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Return trailer information for a given IMDb id if available."""
        params = {"imdb_id": imdb_id, "api_key": settings.KINO_API_KEY}
        data = self.http_client.get("/trailer", params=params)
        # Contract: return None if no trailer found
        return data or None




from __future__ import annotations

from typing import Any, Dict, Optional

from django.conf import settings

from .http_client import HttpClient


class KinoCheckService:
    """Service wrapper for KinoCheck trailer API."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.KINO_BASE)

    def get_trailer(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Return trailer information for a given IMDb id if available.
        
        Uses KinoCheck API endpoint: GET /movies?imdb_id={imdb_id}&language=en&categories=Trailer
        with X-Api-Key header.
        """
        params = {
            "imdb_id": imdb_id,
            "language": "en",
            "categories": "Trailer"
        }
        headers = {"X-Api-Key": settings.KINO_API_KEY}
        try:
            data = self.http_client.get("/movies", params=params, headers=headers)
            # Check if response contains an error (KinoCheck returns 200 with error object)
            if data and isinstance(data, dict):
                error_msg = data.get("message", "").lower()
                if data.get("error") or "not found" in error_msg or "invalid api key" in error_msg:
                    return None
            # Contract: return None if no trailer found
            return data or None
        except Exception:
            # If API call fails, return None instead of raising
            return None




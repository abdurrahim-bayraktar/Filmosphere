from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.conf import settings

from .http_client import HttpClient


class KinoCheckService:
    """Service wrapper for KinoCheck trailer API."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.KINO_BASE)

    def _get_headers(self) -> Dict[str, str]:
        """Get standard KinoCheck API headers."""
        return {
            "X-Api-Key": settings.KINO_API_KEY,
            "X-Api-Host": "api.kinocheck.com",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

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
        headers = self._get_headers()
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

    def get_latest_trailers(self) -> List[Dict[str, Any]]:
        """Get latest trailers from KinoCheck."""
        headers = self._get_headers()
        try:
            data = self.http_client.get("/trailers/latest", headers=headers)
            if data and isinstance(data, dict):
                return data.get("results", []) or []
            return data or []
        except Exception:
            return []

    def get_trending_trailers(self) -> List[Dict[str, Any]]:
        """Get trending trailers from KinoCheck."""
        headers = self._get_headers()
        try:
            data = self.http_client.get("/trailers/trending", headers=headers)
            if data and isinstance(data, dict):
                return data.get("results", []) or []
            return data or []
        except Exception:
            return []

    def get_trailers_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Get trailers filtered by genre."""
        headers = self._get_headers()
        params = {"genres": genre}
        try:
            data = self.http_client.get("/trailers", params=params, headers=headers)
            if data and isinstance(data, dict):
                return data.get("results", []) or []
            return data or []
        except Exception:
            return []

    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Get movie details by KinoCheck movie ID."""
        headers = self._get_headers()
        params = {"id": movie_id}
        try:
            data = self.http_client.get("/movies", params=params, headers=headers)
            if data and isinstance(data, dict):
                error_msg = data.get("message", "").lower()
                if data.get("error") or "not found" in error_msg:
                    return None
            return data or None
        except Exception:
            return None




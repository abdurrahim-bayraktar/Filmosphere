from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from .http_client import HttpClient

logger = logging.getLogger(__name__)

class KinoCheckService:
    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.KINO_BASE)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Api-Key": settings.KINO_API_KEY,
            "Accept": "application/json",
        }

    def _format_response(self, data: Any) -> List[Dict[str, Any]]:
        if not data:
            return []
        if isinstance(data, dict):
            if "0" in data:
                return list(data.values())
            return data.get("results") or data.get("trailers") or []
        if isinstance(data, list):
            return data
        return []

    def get_latest_trailers(self) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        try:
            data = self.http_client.get("/trailers/latest", headers=headers)
            return self._format_response(data)
        except Exception as e:
            logger.error(f"KinoCheck latest error: {e}")
            return []

    def get_trending_trailers(self) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        try:
            data = self.http_client.get("/trailers/trending", headers=headers)
            return self._format_response(data)
        except Exception as e:
            logger.error(f"KinoCheck trending error: {e}")
            return []

    def get_trailers_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        params = {"genres": genre}
        try:
            data = self.http_client.get("/trailers", params=params, headers=headers)
            return self._format_response(data)
        except Exception as e:
            logger.error(f"KinoCheck genre error: {e}")
            return []

    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        headers = self._get_headers()
        params = {"id": movie_id}
        try:
            data = self.http_client.get("/movies", params=params, headers=headers)
            if isinstance(data, dict) and (data.get("error") or not data):
                return None
            return data
        except Exception as e:
            logger.error(f"KinoCheck ID error: {e}")
            return None
        

    def get_kinocheck_url_by_imdb_id(self, imdb_id: str, language: str = "en") -> Optional[str]:
        """
        Fetches the KinoCheck Trailer URL for a specific movie using its IMDb ID.
        """
        headers = self._get_headers()
        params = {
            "imdb_id": imdb_id,
            "language": language
        }

        try:
            data = self.http_client.get("/movies", headers=headers, params=params)
            
            if isinstance(data, dict):
                # SAFE ACCESS: 
                # Use (data.get("trailer") or {}) to handle if the value is None
                trailer_data = data.get("trailer") or {}
                
                return trailer_data.get("url")
            
            return None

        except Exception as e:
            # Note: Make sure 'logger' is imported or defined in this file
            logger.error(f"KinoCheck trailer lookup error for IMDb ID {imdb_id}: {e}")
            return None
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from django.http import Http404

from core.services import IMDbService, KinoCheckService, WatchmodeService
from .film_cache import FilmCacheService

IMDB_ID_PATTERN = re.compile(r"^tt\d+$")


class FilmAggregatorService:
    """Aggregate data from external services and manage caching."""

    def __init__(
        self,
        imdb_service: Optional[IMDbService] = None,
        kino_service: Optional[KinoCheckService] = None,
        watchmode_service: Optional[WatchmodeService] = None,
        cache_service: Optional[FilmCacheService] = None,
    ) -> None:
        self.imdb_service = imdb_service or IMDbService()
        self.kino_service = kino_service or KinoCheckService()
        self.watchmode_service = watchmode_service or WatchmodeService()
        self.cache_service = cache_service or FilmCacheService()

    def fetch_and_cache(self, imdb_id: str) -> Dict[str, Any]:
        """Return aggregated payload for the given IMDb id, using cache when valid.

        The method validates the IMDb id, checks cache freshness, and on cache miss
        or stale data, fetches from all external services, merges the result,
        persists it, and returns the combined payload including any warnings.
        """
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")

        if self.cache_service.is_fresh(imdb_id):
            cached = self.cache_service.get_cached(imdb_id)
            if cached:
                return cached

        warnings: List[str] = []
        metadata: Dict[str, Any] = {}
        credits: Dict[str, Any] = {}
        images: Dict[str, Any] = {}
        videos: Dict[str, Any] = {}
        parents_guide: Dict[str, Any] = {}
        certificates: Dict[str, Any] = {}
        release_dates: Dict[str, Any] = {}
        trailer: Optional[Dict[str, Any]] = None
        streaming: List[Dict[str, Any]] = []

        # IMDb group
        try:
            metadata = self.imdb_service.get_metadata(imdb_id)
        except Exception:  # noqa: BLE001
            raise Http404("Film not found in IMDb")

        try:
            credits = self.imdb_service.get_credits(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("credits_unavailable")

        try:
            images = self.imdb_service.get_images(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("images_unavailable")

        try:
            videos = self.imdb_service.get_videos(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("videos_unavailable")

        try:
            parents_guide = self.imdb_service.get_parents_guide(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("parents_guide_unavailable")

        try:
            certificates = self.imdb_service.get_certificates(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("certificates_unavailable")

        try:
            release_dates = self.imdb_service.get_release_dates(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("release_dates_unavailable")

        # KinoCheck trailer
        try:
            trailer = self.kino_service.get_trailer(imdb_id)
        except Exception:  # noqa: BLE001
            warnings.append("trailer_unavailable")

        # Watchmode streaming
        try:
            title_id = self.watchmode_service.lookup_title_id(imdb_id)
            if title_id is not None:
                streaming = self.watchmode_service.get_streaming_sources(title_id)
        except Exception:  # noqa: BLE001
            warnings.append("streaming_unavailable")

        payload: Dict[str, Any] = {
            "imdb_id": imdb_id,
            "title": metadata.get("title"),
            "metadata": metadata,
            "credits": credits,
            "images": images,
            "videos": videos,
            "parents_guide": parents_guide,
            "certificates": certificates,
            "release_dates": release_dates,
            "trailer": trailer,
            "streaming": streaming,
            "warnings": warnings,
        }

        self.cache_service.save_cache(imdb_id, payload)
        return payload




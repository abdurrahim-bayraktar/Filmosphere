from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone

from films.models import Film


class FilmCacheService:
    """Service responsible for reading and writing cached film payloads."""

    def get_cached(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Return cached payload for the given IMDb id if present."""
        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return None
        return film.full_json

    def save_cache(self, imdb_id: str, payload: Dict[str, Any]) -> None:
        """Persist the given payload into the Film cache row."""
        metadata = payload.get("metadata", {})
        
        # Extract title - try primaryTitle first, then title at root level
        title = metadata.get("primaryTitle") or payload.get("title") or ""
        
        # Extract year - try startYear first, then year in metadata
        year = metadata.get("startYear") or metadata.get("year")
        
        # Extract poster URL
        poster_url = metadata.get("poster_url") or metadata.get("primaryImage", {}).get("url")
        
        defaults = {
            "title": title,
            "year": year,
            "poster_url": poster_url,
            "full_json": payload,
            "cached_at": timezone.now(),
        }
        Film.objects.update_or_create(imdb_id=imdb_id, defaults=defaults)

    def is_fresh(self, imdb_id: str) -> bool:
        """Return True if the cached record is within the configured TTL."""
        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return False
        if not film.cached_at:
            return False
        ttl_hours = getattr(settings, "CACHE_TTL_HOURS", 24)
        return film.cached_at + timedelta(hours=ttl_hours) > timezone.now()




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
        # Extract poster URL from metadata.primaryImage.url (IMDb format)
        primary_image = metadata.get("primaryImage")
        poster_url = None
        if isinstance(primary_image, dict):
            poster_url = primary_image.get("url")
        elif isinstance(primary_image, str):
            poster_url = primary_image
        # Fallback to metadata.poster_url if primaryImage is not available
        if not poster_url:
            poster_url = metadata.get("poster_url")
        
        # Extract title from payload or metadata
        title = payload.get("title") or metadata.get("primaryTitle") or metadata.get("title") or ""
        
        defaults = {
            "title": title,
            "year": metadata.get("startYear") or metadata.get("year"),
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




import uuid

from django.db import models


class Film(models.Model):
    """Persistent cache of aggregated film data keyed by IMDb id."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imdb_id = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=512, db_index=True)
    year = models.IntegerField(null=True, blank=True)
    poster_url = models.URLField(max_length=2000, null=True, blank=True)
    full_json = models.JSONField(null=True, blank=True)
    cached_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["imdb_id"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.imdb_id})"




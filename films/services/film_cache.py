# films/services/film_cache.py

class FilmCacheService:
    """
    Stores film data into PostgreSQL and handles TTL-based invalidation.
    """

    CACHE_TTL_HOURS = 72

    def is_cached(self, imdb_id: str) -> bool:
        pass

    def get_cached(self, imdb_id: str) -> dict:
        pass

    def save_cache(self, imdb_id: str, full_data: dict):
        pass

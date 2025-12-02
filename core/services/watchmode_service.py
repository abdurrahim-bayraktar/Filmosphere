# core/services/watchmode_service.py

class WatchmodeService:
    BASE_URL = "https://api.watchmode.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def lookup_title_id(self, imdb_id: str) -> int:
        """GET /search/?search_field=imdb_id"""
        pass

    def get_streaming_sources(self, title_id: int) -> list:
        """GET /title/{id}/sources/?regions=TR"""
        pass

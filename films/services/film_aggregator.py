# films/services/film_aggregator.py

from core.services.imdb_service import IMDbService
from core.services.kinocheck_service import KinoCheckService
from core.services.watchmode_service import WatchmodeService
from core.services.deepseek_service import DeepSeekService


class FilmAggregatorService:

    def __init__(self):
        self.imdb = IMDbService()
        self.kino = KinoCheckService()
        self.watchmode = WatchmodeService(api_key="SET IN SETTINGS")
        self.deepseek = DeepSeekService()

    def fetch_full_film_data(self, imdb_id: str) -> dict:
        """
        Returns unified film structure combining:
        - IMDb metadata
        - Credits
        - Images
        - Videos
        - Parents guide
        - Certificates
        - Release dates
        - Trailer (KinoCheck)
        - Streaming sources (Watchmode TR)
        - Recommendations (DeepSeek)
        """
        pass

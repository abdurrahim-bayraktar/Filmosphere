# core/services/kinocheck_service.py

class KinoCheckService:
    BASE_URL = "https://api.kinocheck.com"

    def get_trailer(self, imdb_id: str) -> dict:
        """
        GET /movies?imdb_id={imdb_id}&language=en&categories=Trailer
        """
        pass

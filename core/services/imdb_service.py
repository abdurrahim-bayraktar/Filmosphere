# core/services/imdb_service.py

class IMDbService:
    BASE_URL = "https://api.imdbapi.dev"

    def get_metadata(self, imdb_id: str) -> dict:
        """GET /titles/{id}"""
        pass

    def get_credits(self, imdb_id: str) -> dict:
        """GET /titles/{id}/credits"""
        pass

    def get_images(self, imdb_id: str) -> dict:
        """GET /titles/{id}/images"""
        pass

    def get_videos(self, imdb_id: str) -> dict:
        """GET /titles/{id}/videos"""
        pass

    def get_parents_guide(self, imdb_id: str) -> dict:
        """GET /titles/{id}/parentsGuide"""
        pass

    def get_certificates(self, imdb_id: str) -> dict:
        """GET /titles/{id}/certificates"""
        pass

    def get_release_dates(self, imdb_id: str) -> dict:
        """GET /titles/{id}/releaseDates"""
        pass

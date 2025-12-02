# core/services/deepseek_service.py

class DeepSeekService:
    BASE_URL = "https://api.deepseek.com"

    def get_recommendations(self, film_data: dict) -> list:
        """
        Use film metadata to generate embeddings/content-based recommendations.
        """
        pass

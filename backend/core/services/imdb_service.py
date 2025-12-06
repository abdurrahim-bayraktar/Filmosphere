from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from django.conf import settings

from .http_client import HttpClient


class IMDbService:
    """Service wrapper for IMDbAPI.dev endpoints."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        self.http_client = http_client or HttpClient(base_url=settings.IMDBAPI_BASE)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search films by text query using IMDbAPI `/search/titles`.

        This normalizes the external response into a simple list of
        {imdb_id, title, year, image, type} dictionaries suitable for the
        public search endpoint.
        """
        try:
            payload = self.http_client.get(
                "/search/titles",
                params={"query": query, "limit": 10},
            )
        except httpx.HTTPError:
            # Treat network / client errors as "no results" for now.
            return []
        titles = payload.get("titles", []) or []
        normalized: List[Dict[str, Any]] = []
        for item in titles:
            primary_image = item.get("primaryImage") or {}
            normalized.append(
                {
                    "imdb_id": item.get("id"),
                    "title": item.get("primaryTitle"),
                    "year": item.get("startYear"),
                    "image": primary_image.get("url"),
                    "type": item.get("type"),
                }
            )
        return normalized

    def get_metadata(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch core metadata for a film."""
        return self.http_client.get(f"/titles/{imdb_id}")

    def get_credits(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch credits information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/credits")

    def get_images(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch image gallery for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/images")

    def get_videos(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch related videos for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/videos")

    def get_parents_guide(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch parents guide information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/parentsGuide")

    def get_certificates(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch certification information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/certificates")

    def get_release_dates(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch release date information for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/releaseDates")

    def get_akas(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch different names/alternate titles (AKAs) for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/akas")

    def get_seasons(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch season count for a TV series."""
        return self.http_client.get(f"/titles/{imdb_id}/seasons")

    def get_episodes(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch episodes for a TV series."""
        return self.http_client.get(f"/titles/{imdb_id}/episodes")

    def get_award_nominations(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch award nominations for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/awardNominations")

    def get_company_credits(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch company credits for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/companyCredits")

    def get_box_office(self, imdb_id: str) -> Dict[str, Any]:
        """Fetch box office data for a film."""
        return self.http_client.get(f"/titles/{imdb_id}/boxOffice")

    def search_movies_graphql(self, query: str) -> Dict[str, Any]:
        """Search movies using GraphQL query (alternative search method).
        
        Args:
            query: Search term (e.g., "avengers")
        
        Returns:
            GraphQL response with movie results
        """
        # Build GraphQL query string
        graphql_query_string = f'query {{ movies(query: "{query}") {{ results {{ imdbId title year type }} }} }}'
        graphql_payload = {
            "query": graphql_query_string
        }
        return self.http_client.post("/titles", json=graphql_payload)




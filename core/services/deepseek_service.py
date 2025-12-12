from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from django.conf import settings

from core.services.http_client import HttpClient

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Service for generating film recommendations using DeepSeek API (FR11)."""

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, http_client: HttpClient | None = None):
        self.http_client = http_client or HttpClient()
        self.api_key = getattr(settings, "DEEPSEEK_API_KEY", "")

    def get_recommendations(
        self,
        user_ratings: List[Dict[str, Any]],
        user_moods: List[Dict[str, Any]],
        viewing_history: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Generate personalized film recommendations based on user data (FR11.1, FR11.2).
        
        Args:
            user_ratings: List of user's ratings with film info
            user_moods: List of user's mood logs
            viewing_history: List of films user has watched
            
        Returns:
            List of recommended film titles
        """
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
            return []

        # Build prompt with user data
        prompt = self._build_recommendation_prompt(user_ratings, user_moods, viewing_history)

        try:
            response = self._call_deepseek_api(prompt)
            film_titles = self._parse_recommendations(response)
            return film_titles
        except Exception as e:
            logger.error(f"Error getting recommendations from DeepSeek: {e}")
            return []

    def _build_recommendation_prompt(
        self,
        user_ratings: List[Dict[str, Any]],
        user_moods: List[Dict[str, Any]],
        viewing_history: List[Dict[str, Any]],
    ) -> str:
        """Build a prompt for DeepSeek API based on user's data."""
        
        prompt_parts = [
            "You are a film recommendation expert. Based on the following user data, recommend 10 films.",
            "Return ONLY a JSON array of film titles (exact film names), nothing else.",
            "Example format: [\"The Shawshank Redemption\", \"The Dark Knight\", \"Inception\"]",
            "",
            "User's Rating History:",
        ]

        # Add ratings
        if user_ratings:
            for rating in user_ratings[:20]:  # Limit to 20 most recent
                film_title = rating.get("film_title", "Unknown")
                overall = rating.get("overall_rating", "N/A")
                prompt_parts.append(f"- {film_title}: {overall}/5")
        else:
            prompt_parts.append("- No ratings yet")

        prompt_parts.append("")
        prompt_parts.append("User's Mood Patterns:")

        # Add moods
        if user_moods:
            for mood in user_moods[:10]:  # Limit to 10 most recent
                film_title = mood.get("film_title", "Unknown")
                mood_before = mood.get("mood_before", "N/A")
                mood_after = mood.get("mood_after", "N/A")
                prompt_parts.append(f"- {film_title}: {mood_before} → {mood_after}")
        else:
            prompt_parts.append("- No mood logs yet")

        prompt_parts.append("")
        prompt_parts.append("Based on these preferences, recommend 10 films that the user would likely enjoy.")
        prompt_parts.append("Return ONLY a JSON array of film titles.")

        return "\n".join(prompt_parts)

    def _call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """Call DeepSeek API to get recommendations."""
        import httpx
        from django.conf import settings
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")
        
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a film recommendation expert. Always return film recommendations as a JSON array of film titles only. Example: [\"The Shawshank Redemption\", \"The Dark Knight\"]",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        timeout = float(getattr(settings, "HTTP_TIMEOUT", 30))
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def _parse_recommendations(self, response: Dict[str, Any]) -> List[str]:
        """Parse DeepSeek API response to extract film titles."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse as JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON array
            film_titles = json.loads(content)
            if isinstance(film_titles, list):
                return [str(title).strip() for title in film_titles if title]
            
            # If not JSON, try to extract film names from text
            # This is a fallback
            return []
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing DeepSeek response: {e}")
            return []

    def check_spoiler(self, film_title: str, comment_text: str) -> bool:
        """
        Check if a comment contains spoilers for a film (FR06.2).
        
        Args:
            film_title: Title of the film
            comment_text: The comment/review text to check
            
        Returns:
            True if comment contains spoilers, False otherwise
        """
        if not self.api_key:
            logger.warning("DeepSeek API key not configured for spoiler detection")
            return False

        prompt = self._build_spoiler_check_prompt(film_title, comment_text)

        try:
            response = self._call_deepseek_api(prompt)
            is_spoiler = self._parse_spoiler_response(response)
            return is_spoiler
        except Exception as e:
            logger.error(f"Error checking spoiler with DeepSeek: {e}")
            return False

    def _build_spoiler_check_prompt(self, film_title: str, comment_text: str) -> str:
        """Build a prompt for spoiler detection."""
        return f"""You are a spoiler detection system for film reviews.

Film Title: {film_title}

Comment/Review Text:
{comment_text}

Determine if this comment contains spoilers about the film. A spoiler is any information that reveals:
- Major plot points or twists
- Character deaths
- Surprise endings
- Important story revelations
- Key plot developments

Respond with ONLY "YES" if it contains spoilers, or "NO" if it does not contain spoilers.
Do not include any explanation, just "YES" or "NO"."""

    def _parse_spoiler_response(self, response: Dict[str, Any]) -> bool:
        """Parse DeepSeek API response to determine if comment is a spoiler."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            content = content.strip().upper()
            
            # Check if response indicates spoiler
            return "YES" in content or content.startswith("YES")
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing spoiler response: {e}")
            return False

    def moderate_comment(self, comment_text: str, blacklist: List[str] = None) -> Dict[str, Any]:
        """
        Moderate a comment using LLM to check for blacklisted words and inappropriate content.
        
        Args:
            comment_text: The comment/review text to moderate
            blacklist: List of blacklisted words/phrases (optional)
            
        Returns:
            Dict with:
                - needs_moderation: bool (True if comment should be flagged)
                - reason: str (reason for flagging)
                - detected_words: List[str] (blacklisted words found)
        """
        if not self.api_key:
            logger.warning("DeepSeek API key not configured for comment moderation")
            # Fallback to basic blacklist check
            return self._check_blacklist_basic(comment_text, blacklist or [])
        
        # First check blacklist locally (faster)
        blacklist_result = self._check_blacklist_basic(comment_text, blacklist or [])
        if blacklist_result["needs_moderation"]:
            return blacklist_result
        
        # Then use LLM for deeper analysis
        prompt = self._build_moderation_prompt(comment_text, blacklist or [])
        
        try:
            response = self._call_deepseek_api(prompt)
            llm_result = self._parse_moderation_response(response)
            
            # Combine results
            if blacklist_result["detected_words"]:
                llm_result["detected_words"].extend(blacklist_result["detected_words"])
                llm_result["needs_moderation"] = True
                llm_result["reason"] = f"Blacklisted words detected: {', '.join(blacklist_result['detected_words'])}"
            
            return llm_result
        except Exception as e:
            logger.error(f"Error moderating comment with DeepSeek: {e}")
            return blacklist_result

    def _check_blacklist_basic(self, comment_text: str, blacklist: List[str]) -> Dict[str, Any]:
        """Basic blacklist checking without LLM."""
        comment_lower = comment_text.lower()
        detected_words = []
        
        for word in blacklist:
            if word.lower() in comment_lower:
                detected_words.append(word)
        
        return {
            "needs_moderation": len(detected_words) > 0,
            "reason": f"Blacklisted words detected: {', '.join(detected_words)}" if detected_words else "",
            "detected_words": detected_words,
        }

    def _build_moderation_prompt(self, comment_text: str, blacklist: List[str]) -> str:
        """Build a prompt for comment moderation."""
        blacklist_text = ", ".join(blacklist) if blacklist else "None specified"
        
        return f"""You are a content moderation system for film review comments.

Comment to moderate:
{comment_text}

Blacklisted words/phrases: {blacklist_text}

Analyze this comment and determine if it:
1. Contains any blacklisted words or phrases
2. Contains inappropriate content (spam, harassment, hate speech, etc.)
3. Violates community guidelines

Respond with a JSON object in this exact format:
{{
    "needs_moderation": true/false,
    "reason": "Brief reason if needs_moderation is true",
    "detected_words": ["list", "of", "blacklisted", "words", "found"]
}}

If the comment is appropriate, set needs_moderation to false."""

    def _parse_moderation_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse DeepSeek API response for moderation."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            result = json.loads(content)
            
            return {
                "needs_moderation": result.get("needs_moderation", False),
                "reason": result.get("reason", ""),
                "detected_words": result.get("detected_words", []),
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing moderation response: {e}")
            return {
                "needs_moderation": False,
                "reason": "",
                "detected_words": [],
            }


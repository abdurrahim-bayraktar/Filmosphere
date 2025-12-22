from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from django.conf import settings
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client wrapper around httpx with retry and timeout support.

    This client is designed to be dependency-injected into services so that
    external calls can be easily mocked in tests.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout or float(getattr(settings, "HTTP_TIMEOUT", 10))
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(getattr(settings, "HTTP_RETRIES", 3)),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform a GET request and return the decoded JSON payload.

        Args:
            url: Relative or absolute URL to fetch.
            params: Optional query parameters.
            headers: Optional HTTP headers.

        Returns:
            Parsed JSON response as a dictionary.
        """
        response = self._client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, url: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform a POST request and return the decoded JSON payload.

        Args:
            url: Relative or absolute URL to fetch.
            json: Optional JSON body to send.
            headers: Optional HTTP headers.

        Returns:
            Parsed JSON response as a dictionary.
        """
        response = self._client.post(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()




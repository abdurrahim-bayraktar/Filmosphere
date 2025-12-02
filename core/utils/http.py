# core/utils/http.py

class HTTPClient:
    """
    A wrapper for requests with:
    - timeout
    - retries
    - backoff
    - error handling
    """

    def get(self, url: str, params: dict = None, headers: dict = None):
        pass

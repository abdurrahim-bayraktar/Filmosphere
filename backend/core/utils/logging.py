import logging
from typing import Any, Dict, Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger for the given name."""
    return logging.getLogger(name or __name__)


def log_json(logger: logging.Logger, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log a structured JSON-like message.

    This keeps things simple while still keeping logs structured for later parsing.
    """
    payload = {"message": message}
    if extra:
        payload.update(extra)
    logger.log(level, payload)




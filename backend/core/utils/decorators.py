from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


def log_exceptions(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that logs exceptions while letting them propagate.

    This is primarily useful around service-layer methods.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:  # type: ignore[override]
        try:
            return func(*args, **kwargs)
        except Exception:  # noqa: BLE001
            logger.exception("Unhandled exception in %s", func.__name__)
            raise

    return wrapper




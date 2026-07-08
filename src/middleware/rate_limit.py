"""Rate limiting en memoria para endpoints sensibles."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

_buckets: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def check_rate_limit(key: str, *, max_attempts: int, window_seconds: int) -> bool:
    """Devuelve True si la petición está permitida."""
    now = time.time()
    cutoff = now - window_seconds
    with _lock:
        hits = [t for t in _buckets[key] if t > cutoff]
        if len(hits) >= max_attempts:
            _buckets[key] = hits
            return False
        hits.append(now)
        _buckets[key] = hits
        return True


def reset_rate_limit(key: str) -> None:
    with _lock:
        _buckets.pop(key, None)


def reset_all_rate_limits() -> None:
    """Solo para tests — limpia contadores in-process."""
    with _lock:
        _buckets.clear()

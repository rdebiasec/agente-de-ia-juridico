"""Helpers compartidos de timeout, reintento y presupuesto."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from src.config import get_settings

T = TypeVar("T")

_TRANSIENT_ERROR_NAMES = frozenset(
    {
        "APITimeoutError",
        "APIConnectionError",
        "RateLimitError",
        "InternalServerError",
        "ServiceUnavailableError",
        "TimeoutError",
        "CancelledError",
    }
)


def is_transient_error(exc: BaseException) -> bool:
    """Clasifica errores reintentables sin acoplarse a la SDK de OpenAI."""
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError, ConnectionError)):
        return True
    name = type(exc).__name__
    if name in _TRANSIENT_ERROR_NAMES:
        return True
    # Algunas librerías anidan el error original.
    cause = getattr(exc, "__cause__", None)
    if cause is not None and cause is not exc:
        return is_transient_error(cause)
    return False


def retry_delay_seconds(attempt: int) -> float:
    """Backoff exponencial acotado con jitter anti thundering-herd."""
    base = min(2**attempt, 4)
    return base + random.uniform(0.0, 0.5 * base)


async def run_with_retries(
    operation: Callable[[], Awaitable[T]],
    *,
    max_retries: int | None = None,
    timeout_seconds: float | None = None,
    on_retry: Callable[[int, BaseException, float], Awaitable[None] | None] | None = None,
    non_retryable: tuple[type[BaseException], ...] = (),
) -> T:
    """Ejecuta una corrutina con timeout, reintento y jitter."""
    settings = get_settings()
    attempts = max(1, (settings.agent_max_retries if max_retries is None else max_retries) + 1)
    last_exc: BaseException | None = None
    for attempt in range(attempts):
        try:
            if timeout_seconds and timeout_seconds > 0:
                return await asyncio.wait_for(operation(), timeout=timeout_seconds)
            return await operation()
        except non_retryable:
            raise
        except Exception as exc:  # noqa: BLE001 — filtrado por is_transient_error
            last_exc = exc
            if attempt + 1 >= attempts or not is_transient_error(exc):
                raise
            delay = retry_delay_seconds(attempt)
            if on_retry is not None:
                maybe = on_retry(attempt, exc, delay)
                if asyncio.iscoroutine(maybe):
                    await maybe
            await asyncio.sleep(delay)
    assert last_exc is not None  # pragma: no cover
    raise last_exc

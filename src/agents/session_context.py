"""Contexto de sesión para tools de grounding (evita IDOR entre expedientes)."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

_active_session_id: ContextVar[str | None] = ContextVar(
    "active_expediente_session_id",
    default=None,
)


def get_active_session_id() -> str | None:
    return _active_session_id.get()


@contextmanager
def bind_active_session(session_id: str | None) -> Iterator[None]:
    """Fija el expediente de la corrutina actual para tools de búsqueda."""
    token = _active_session_id.set((session_id or "").strip() or None)
    try:
        yield
    finally:
        _active_session_id.reset(token)


def resolve_expediente_id(requested: str | None = None) -> str | None:
    """Solo permite el expediente de la sesión activa.

    Si el modelo pide otro ID, se ignora y se usa el de la sesión. Sin sesión
    activa no se permite búsqueda cruzada.
    """
    active = get_active_session_id()
    if not active:
        return None
    requested_id = (requested or "").strip()
    if requested_id and requested_id != active:
        return None
    return active

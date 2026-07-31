"""Contexto de sesión / RunContext tipado (anti-IDOR entre expedientes)."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class FirmRunContext:
    """Carpeta tipada del caso para Runner.run(..., context=).

    Sin secrets ni PII libre: solo IDs y flags de cumplimiento.
    """

    session_id: str
    expediente_id: str
    channel: str = "web"
    user_id: str = ""
    involucra_menor: bool = False
    datos_sensibles: bool = False


_active_session_id: ContextVar[str | None] = ContextVar(
    "active_expediente_session_id",
    default=None,
)
_active_run_context: ContextVar[FirmRunContext | None] = ContextVar(
    "active_firm_run_context",
    default=None,
)


def get_active_session_id() -> str | None:
    return _active_session_id.get()


def get_active_run_context() -> FirmRunContext | None:
    return _active_run_context.get()


@contextmanager
def bind_active_session(session_id: str | None) -> Iterator[None]:
    """Fija el expediente de la corrutina actual para tools de búsqueda."""
    token = _active_session_id.set((session_id or "").strip() or None)
    try:
        yield
    finally:
        _active_session_id.reset(token)


@contextmanager
def bind_run_context(ctx: FirmRunContext | None) -> Iterator[None]:
    """Enlaza RunContext tipado + session_id (compat tools / resolve_expediente_id)."""
    session_token = _active_session_id.set(
        (ctx.expediente_id if ctx else None) or (ctx.session_id if ctx else None) or None
    )
    ctx_token = _active_run_context.set(ctx)
    try:
        yield
    finally:
        _active_run_context.reset(ctx_token)
        _active_session_id.reset(session_token)


def resolve_expediente_id(requested: str | None = None) -> str | None:
    """Solo permite el expediente de la sesión / RunContext activo.

    Si el modelo pide otro ID, se ignora y se usa el del contexto. Sin sesión
    activa no se permite búsqueda cruzada.
    """
    run_ctx = get_active_run_context()
    active = (run_ctx.expediente_id if run_ctx else None) or get_active_session_id()
    if not active:
        return None
    requested_id = (requested or "").strip()
    if requested_id and requested_id != active:
        return None
    return active

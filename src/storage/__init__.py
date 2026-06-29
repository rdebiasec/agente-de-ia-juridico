"""Selector de backend de persistencia.

`DATABASE_URL` vacío  -> repositorio en memoria (tests / local sin Docker).
`DATABASE_URL` con valor -> Postgres/pgvector (Docker / Render): paridad dev==prod.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from src.storage.base import Repository
from src.storage.memory import InMemoryRepository
from src.storage.models import Deadline, DocumentChunk, Draft, Expediente

logger = logging.getLogger(__name__)

__all__ = [
    "Repository",
    "InMemoryRepository",
    "Draft",
    "Deadline",
    "DocumentChunk",
    "Expediente",
    "get_repository",
    "reset_repository",
]


@lru_cache(maxsize=1)
def _build_repository() -> Repository:
    from src.config import get_settings

    settings = get_settings()
    if settings.database_url:
        from src.storage.sql import SqlRepository

        repo = SqlRepository(settings.database_url)
        try:
            from src.storage.migrate import run_migrations

            run_migrations(settings.database_url)
        except Exception:
            logger.exception("Migraciones Alembic fallaron; uso ensure_schema como fallback")
            repo.ensure_schema()
        return repo
    return InMemoryRepository()


def get_repository() -> Repository:
    return _build_repository()


def reset_repository() -> None:
    """Limpia el singleton (útil en tests que cambian DATABASE_URL)."""
    _build_repository.cache_clear()

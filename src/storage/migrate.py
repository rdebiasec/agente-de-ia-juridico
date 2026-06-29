"""Ejecuta migraciones Alembic de forma programática (arranque de la app)."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from src.storage.sql import normalize_database_url

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_PROJECT_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", normalize_database_url(database_url))
    return cfg


def run_migrations(database_url: str) -> None:
    command.upgrade(_alembic_config(database_url), "head")

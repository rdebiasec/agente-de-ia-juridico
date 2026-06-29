"""Expediente como contexto compartido del caso.

La interfaz `ExpedienteStore` se mantiene estable; el backend ahora delega en el
repositorio (`src/storage/`): en memoria (tests/local) o Postgres si hay
`DATABASE_URL`. El modelo `Expediente` vive en `src/storage/models.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.storage import Repository, get_repository
from src.storage.models import MATERIAS, Expediente

__all__ = ["Expediente", "ExpedienteStore", "MATERIAS", "expediente_store"]


@dataclass
class ExpedienteStore:
    """Fachada por sesión sobre el repositorio (reemplaza el dict en memoria)."""

    repo: Repository | None = field(default=None)

    def _repo(self) -> Repository:
        return self.repo or get_repository()

    def get(self, session_id: str) -> Expediente | None:
        return self._repo().get_expediente(session_id)

    def get_or_create(self, session_id: str) -> Expediente:
        exp = self._repo().get_expediente(session_id)
        if exp is None:
            exp = Expediente(session_id=session_id)
            self._repo().save_expediente(exp)
        return exp

    def update(self, session_id: str, **campos) -> Expediente:
        exp = self.get_or_create(session_id)
        for clave, valor in campos.items():
            if hasattr(exp, clave) and valor is not None:
                setattr(exp, clave, valor)
        import time

        exp.actualizado_en = time.time()
        return self._repo().save_expediente(exp)


expediente_store = ExpedienteStore()

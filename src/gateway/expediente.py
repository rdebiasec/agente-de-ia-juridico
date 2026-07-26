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
            exp = self._repo().mutate_expediente(session_id, lambda _: None)
        return exp

    def update(self, session_id: str, **campos) -> Expediente:
        import time

        def _apply(exp: Expediente) -> None:
            for clave, valor in campos.items():
                if hasattr(exp, clave) and valor is not None:
                    setattr(exp, clave, valor)
            exp.actualizado_en = time.time()

        return self._repo().mutate_expediente(session_id, _apply)

    def mutate(self, session_id: str, mutator) -> Expediente:
        """Actualización atómica para listas/métricas compartidas."""
        return self._repo().mutate_expediente(session_id, mutator)


expediente_store = ExpedienteStore()

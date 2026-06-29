"""Interfaz del repositorio de persistencia de la firma.

Permite intercambiar el backend (memoria para tests/local sin Docker,
Postgres/pgvector para paridad dev==prod) sin tocar la lógica de negocio.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.storage.models import Deadline, DocumentChunk, Draft, Expediente


@runtime_checkable
class Repository(Protocol):
    # --- Borradores (HITL) ---
    def add_draft(self, draft: Draft) -> Draft: ...

    def get_draft(self, draft_id: str) -> Draft | None: ...

    def list_drafts(
        self, *, estado: str | None = None, session_id: str | None = None
    ) -> list[Draft]: ...

    def update_draft(self, draft_id: str, **changes) -> Draft | None: ...

    # --- Términos / plazos ---
    def add_deadline(self, deadline: Deadline) -> Deadline: ...

    def list_deadlines(
        self, *, session_id: str | None = None, solo_pendientes: bool = False
    ) -> list[Deadline]: ...

    def update_deadline(self, deadline_id: str, **changes) -> Deadline | None: ...

    # --- RAG (fragmentos + embeddings) ---
    def add_chunk(self, chunk: DocumentChunk) -> DocumentChunk: ...

    def add_chunks(self, chunks: list[DocumentChunk]) -> int: ...

    def buscar_similares(
        self,
        embedding: list[float],
        *,
        expediente_id: str | None = None,
        incluir_kb: bool = True,
        k: int = 5,
    ) -> list[DocumentChunk]: ...

    def contar_chunks(
        self, *, scope: str | None = None, expediente_id: str | None = None, fuente: str | None = None
    ) -> int: ...

    # --- Expediente ---
    def get_expediente(self, session_id: str) -> Expediente | None: ...

    def save_expediente(self, expediente: Expediente) -> Expediente: ...

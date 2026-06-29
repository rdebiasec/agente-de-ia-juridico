"""Backend en memoria (tests y desarrollo local sin Docker)."""

from __future__ import annotations

import math
import threading
from datetime import datetime, timezone

from src.storage.models import Deadline, DocumentChunk, Draft, Expediente, SCOPE_KB


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return -1.0
    return dot / (na * nb)


class InMemoryRepository:
    def __init__(self) -> None:
        self._drafts: dict[str, Draft] = {}
        self._deadlines: dict[str, Deadline] = {}
        self._chunks: dict[str, DocumentChunk] = {}
        self._expedientes: dict[str, Expediente] = {}
        self._lock = threading.Lock()

    # --- Borradores ---
    def add_draft(self, draft: Draft) -> Draft:
        with self._lock:
            self._drafts[draft.id] = draft
        return draft

    def get_draft(self, draft_id: str) -> Draft | None:
        return self._drafts.get(draft_id)

    def list_drafts(
        self, *, estado: str | None = None, session_id: str | None = None
    ) -> list[Draft]:
        items = list(self._drafts.values())
        if estado is not None:
            items = [d for d in items if d.estado == estado]
        if session_id is not None:
            items = [d for d in items if d.session_id == session_id]
        return sorted(items, key=lambda d: d.created_at, reverse=True)

    def update_draft(self, draft_id: str, **changes) -> Draft | None:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                return None
            for key, value in changes.items():
                if hasattr(draft, key):
                    setattr(draft, key, value)
            draft.updated_at = datetime.now(timezone.utc)
            return draft

    # --- Términos ---
    def add_deadline(self, deadline: Deadline) -> Deadline:
        with self._lock:
            self._deadlines[deadline.id] = deadline
        return deadline

    def list_deadlines(
        self, *, session_id: str | None = None, solo_pendientes: bool = False
    ) -> list[Deadline]:
        items = list(self._deadlines.values())
        if session_id is not None:
            items = [d for d in items if d.session_id == session_id]
        if solo_pendientes:
            items = [d for d in items if d.estado == "pendiente"]
        return sorted(items, key=lambda d: (d.fecha_limite or d.created_at.date()))

    def update_deadline(self, deadline_id: str, **changes) -> Deadline | None:
        with self._lock:
            deadline = self._deadlines.get(deadline_id)
            if deadline is None:
                return None
            for key, value in changes.items():
                if hasattr(deadline, key):
                    setattr(deadline, key, value)
            return deadline

    # --- RAG ---
    def add_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        with self._lock:
            self._chunks[chunk.id] = chunk
        return chunk

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        with self._lock:
            for chunk in chunks:
                self._chunks[chunk.id] = chunk
        return len(chunks)

    def buscar_similares(
        self,
        embedding: list[float],
        *,
        expediente_id: str | None = None,
        incluir_kb: bool = True,
        k: int = 5,
    ) -> list[DocumentChunk]:
        candidatos: list[DocumentChunk] = []
        for chunk in self._chunks.values():
            if chunk.scope == SCOPE_KB:
                if not incluir_kb:
                    continue
            elif expediente_id is not None and chunk.expediente_id != expediente_id:
                continue
            elif expediente_id is None:
                # Sin expediente solicitado, solo se busca en la KB global.
                continue
            candidatos.append(chunk)

        puntuados = []
        for chunk in candidatos:
            score = _cosine(embedding, chunk.embedding)
            copia = DocumentChunk(
                id=chunk.id,
                scope=chunk.scope,
                expediente_id=chunk.expediente_id,
                fuente=chunk.fuente,
                chunk_text=chunk.chunk_text,
                embedding=[],
                metadata=chunk.metadata,
                created_at=chunk.created_at,
                score=score,
            )
            puntuados.append(copia)
        puntuados.sort(key=lambda c: c.score or -1.0, reverse=True)
        return puntuados[:k]

    def contar_chunks(
        self, *, scope: str | None = None, expediente_id: str | None = None, fuente: str | None = None
    ) -> int:
        total = 0
        for chunk in self._chunks.values():
            if scope is not None and chunk.scope != scope:
                continue
            if expediente_id is not None and chunk.expediente_id != expediente_id:
                continue
            if fuente is not None and chunk.fuente != fuente:
                continue
            total += 1
        return total

    # --- Expediente ---
    def get_expediente(self, session_id: str) -> Expediente | None:
        return self._expedientes.get(session_id)

    def save_expediente(self, expediente: Expediente) -> Expediente:
        with self._lock:
            self._expedientes[expediente.session_id] = expediente
        return expediente

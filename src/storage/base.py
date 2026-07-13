"""Interfaz del repositorio de persistencia de la firma.

Permite intercambiar el backend (memoria para tests/local sin Docker,
Postgres/pgvector para paridad dev==prod) sin tocar la lógica de negocio.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.storage.models import (
    AuditPortalAccessLog,
    AuditPortalProgress,
    AuditPortalUser,
    ChatSession,
    ComplianceConsent,
    Deadline,
    DocumentChunk,
    Draft,
    ExecutionPlanRecord,
    Expediente,
    SessionTrace,
)


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

    # --- Conversación y trazas ---
    def get_chat_session(self, session_id: str) -> ChatSession | None: ...

    def save_chat_session(self, session: ChatSession) -> ChatSession: ...

    def append_chat_message(
        self, session_id: str, *, channel: str, user_id: str, role: str, content: str, max_messages: int
    ) -> ChatSession: ...

    def add_session_trace(self, trace: SessionTrace) -> SessionTrace: ...

    def list_session_traces(self, session_id: str, *, limit: int = 50) -> list[SessionTrace]: ...

    def list_recent_session_traces(self, *, limit: int = 50) -> list[SessionTrace]: ...

    def list_chat_sessions(self, *, limit: int = 30) -> list[ChatSession]: ...

    def reset_chat_session(self, session_id: str) -> bool: ...

    def clear_session_traces(self, session_id: str) -> int: ...

    # --- Portal de auditoría ---
    def get_audit_portal_progress(self, email: str) -> AuditPortalProgress | None: ...

    def save_audit_portal_progress(self, email: str, payload: dict) -> AuditPortalProgress: ...

    def delete_audit_portal_progress(self, email: str) -> bool: ...

    def get_audit_portal_user(self, email: str) -> AuditPortalUser | None: ...

    def save_audit_portal_user(self, user: AuditPortalUser) -> AuditPortalUser: ...

    def record_compliance_consent(self, consent: ComplianceConsent) -> ComplianceConsent: ...

    def has_valid_compliance_consent(
        self, subject_key: str, *, context: str, policy_version: str
    ) -> bool: ...

    def log_audit_portal_access(self, entry: AuditPortalAccessLog) -> AuditPortalAccessLog: ...

    def append_audit_progress_history(self, email: str, payload: dict, *, keep_last: int = 60) -> None: ...

    # --- Planes de ejecución (Fase 1) ---
    def get_execution_plan(self, plan_id: str) -> ExecutionPlanRecord | None: ...

    def save_execution_plan(self, record: ExecutionPlanRecord) -> ExecutionPlanRecord: ...

    def list_execution_plans(self, *, limit: int = 50) -> list[ExecutionPlanRecord]: ...

    def execution_plan_stats(self) -> dict: ...

    def clear_all_execution_plans(self) -> int: ...

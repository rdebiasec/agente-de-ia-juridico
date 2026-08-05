"""Backend en memoria (tests y desarrollo local sin Docker)."""

from __future__ import annotations

import math
import threading
from datetime import datetime, timezone

from src.storage.models import (
    AuditPortalAccessLog,
    AuditPortalProgress,
    AuditPortalUser,
    ChatSession,
    ClientMessage,
    ClientThread,
    ComplianceConsent,
    ConfigActive,
    ConfigVersion,
    Deadline,
    DocumentChunk,
    Draft,
    ExecutionPlanRecord,
    Expediente,
    InternalTranscriptEntry,
    OutboundClientDraft,
    SessionTrace,
    SCOPE_KB,
)


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
        self._chat_sessions: dict[str, ChatSession] = {}
        self._session_traces: dict[str, list[SessionTrace]] = {}
        self._audit_progress: dict[str, AuditPortalProgress] = {}
        self._audit_users: dict[str, AuditPortalUser] = {}
        self._compliance_consents: list[ComplianceConsent] = []
        self._execution_plans: dict[str, ExecutionPlanRecord] = {}
        self._audit_access_logs: list[AuditPortalAccessLog] = []
        self._client_threads: dict[str, ClientThread] = {}
        self._client_messages: list[ClientMessage] = []
        self._internal_transcript: list[InternalTranscriptEntry] = []
        self._outbound_client_drafts: dict[str, OutboundClientDraft] = {}
        self._audit_progress_history: list[tuple[str, dict, datetime]] = []
        self._config_versions: list[ConfigVersion] = []
        self._config_active: dict[tuple[str, str], ConfigActive] = {}
        self._config_version_seq = 0
        self._lock = threading.Lock()

    # --- Borradores ---
    def add_draft(self, draft: Draft) -> Draft:
        from src.compliance.crypto_at_rest import encrypt_text
        from copy import copy

        stored = copy(draft)
        stored.contenido = encrypt_text(draft.contenido)
        with self._lock:
            self._drafts[draft.id] = stored
        return draft

    def get_draft(self, draft_id: str) -> Draft | None:
        from src.compliance.crypto_at_rest import decrypt_text
        from copy import copy

        raw = self._drafts.get(draft_id)
        if raw is None:
            return None
        out = copy(raw)
        out.contenido = decrypt_text(raw.contenido)
        return out

    def list_drafts(
        self, *, estado: str | None = None, session_id: str | None = None
    ) -> list[Draft]:
        items = [self.get_draft(d.id) for d in self._drafts.values()]
        items = [d for d in items if d is not None]
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

    def delete_drafts_for_session(self, session_id: str) -> int:
        with self._lock:
            ids = [d.id for d in self._drafts.values() if d.session_id == session_id]
            for did in ids:
                self._drafts.pop(did, None)
            return len(ids)

    def delete_chat_session(self, session_id: str) -> bool:
        with self._lock:
            return self._chat_sessions.pop(session_id, None) is not None

    def delete_expediente(self, session_id: str) -> bool:
        with self._lock:
            return self._expedientes.pop(session_id, None) is not None

    def delete_execution_plans_for_user(self, user_id: str) -> int:
        with self._lock:
            ids = [p.plan_id for p in self._execution_plans.values() if p.initiator_user_id == user_id]
            for pid in ids:
                self._execution_plans.pop(pid, None)
            return len(ids)

    def list_stale_chat_sessions(self, *, older_than, limit: int = 500) -> list[ChatSession]:
        with self._lock:
            items = [s for s in self._chat_sessions.values() if s.updated_at < older_than]
            items.sort(key=lambda s: s.updated_at)
            return items[:limit]

    def list_stale_audit_progress_emails(self, *, older_than, limit: int = 500) -> list[str]:
        with self._lock:
            items = [
                (e, p.updated_at)
                for e, p in self._audit_progress.items()
                if p.updated_at < older_than
            ]
            items.sort(key=lambda x: x[1])
            return [e for e, _ in items[:limit]]

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

    def mutate_expediente(self, session_id: str, mutator) -> Expediente:
        """Read-modify-write atómico dentro del backend en memoria."""
        with self._lock:
            expediente = self._expedientes.get(session_id)
            if expediente is None:
                expediente = Expediente(session_id=session_id)
            mutator(expediente)
            self._expedientes[session_id] = expediente
            return expediente

    # --- Conversación y trazas ---
    def get_chat_session(self, session_id: str) -> ChatSession | None:
        from src.compliance.crypto_at_rest import decrypt_messages
        from copy import copy

        raw = self._chat_sessions.get(session_id)
        if raw is None:
            return None
        out = copy(raw)
        out.messages = decrypt_messages(raw.messages)
        return out

    def save_chat_session(self, session: ChatSession) -> ChatSession:
        from src.compliance.crypto_at_rest import encrypt_messages
        from copy import copy

        stored = copy(session)
        stored.messages = encrypt_messages(session.messages)
        with self._lock:
            self._chat_sessions[session.session_id] = stored
        return session

    def append_chat_message(
        self, session_id: str, *, channel: str, user_id: str, role: str, content: str, max_messages: int
    ) -> ChatSession:
        import time

        from src.compliance.crypto_at_rest import encrypt_text

        now = datetime.now(timezone.utc)
        with self._lock:
            session = self._chat_sessions.get(session_id)
            if session is None:
                session = ChatSession(session_id=session_id, channel=channel, user_id=user_id)
                self._chat_sessions[session_id] = session
            session.messages.append({"role": role, "content": encrypt_text(content), "ts": time.time()})
            if len(session.messages) > max_messages:
                session.messages = session.messages[-max_messages:]
            session.updated_at = now
            session.channel = channel
            session.user_id = user_id
        return self.get_chat_session(session_id) or session

    def add_session_trace(self, trace: SessionTrace) -> SessionTrace:
        with self._lock:
            self._session_traces.setdefault(trace.session_id, []).append(trace)
            bucket = self._session_traces[trace.session_id]
            if len(bucket) > 200:
                self._session_traces[trace.session_id] = bucket[-200:]
        return trace

    def list_session_traces(self, session_id: str, *, limit: int = 50) -> list[SessionTrace]:
        traces = self._session_traces.get(session_id, [])
        return traces[-limit:]

    def list_recent_session_traces(self, *, limit: int = 50) -> list[SessionTrace]:
        with self._lock:
            all_traces: list[SessionTrace] = []
            for bucket in self._session_traces.values():
                all_traces.extend(bucket)
            all_traces.sort(key=lambda t: t.created_at, reverse=True)
            return all_traces[:limit]

    def list_chat_sessions(self, *, limit: int = 30) -> list[ChatSession]:
        with self._lock:
            sessions = list(self._chat_sessions.values())
            sessions.sort(key=lambda s: s.updated_at, reverse=True)
            return sessions[:limit]

    def reset_chat_session(self, session_id: str) -> bool:
        with self._lock:
            session = self._chat_sessions.get(session_id)
            if session is None:
                return False
            session.messages = []
            session.updated_at = datetime.now(timezone.utc)
            return True

    def clear_session_traces(self, session_id: str) -> int:
        with self._lock:
            traces = self._session_traces.pop(session_id, [])
            return len(traces)

    # --- Portal de auditoría ---
    def get_audit_portal_progress(self, email: str) -> AuditPortalProgress | None:
        return self._audit_progress.get(email)

    def save_audit_portal_progress(self, email: str, payload: dict) -> AuditPortalProgress:
        now = datetime.now(timezone.utc)
        with self._lock:
            existing = self._audit_progress.get(email)
            if existing:
                existing.payload = payload
                existing.updated_at = now
                return existing
            row = AuditPortalProgress(email=email, payload=payload, created_at=now, updated_at=now)
            self._audit_progress[email] = row
            return row

    def delete_audit_portal_progress(self, email: str) -> bool:
        with self._lock:
            return self._audit_progress.pop(email, None) is not None

    def get_audit_portal_user(self, email: str) -> AuditPortalUser | None:
        return self._audit_users.get(email)

    def save_audit_portal_user(self, user: AuditPortalUser) -> AuditPortalUser:
        with self._lock:
            self._audit_users[user.email] = user
            return user

    def record_compliance_consent(self, consent: ComplianceConsent) -> ComplianceConsent:
        with self._lock:
            self._compliance_consents.append(consent)
            return consent

    def has_valid_compliance_consent(
        self, subject_key: str, *, context: str, policy_version: str
    ) -> bool:
        for row in reversed(self._compliance_consents):
            if (
                row.subject_key == subject_key
                and row.context == context
                and row.policy_version == policy_version
                and row.privacy_accepted
                and row.sensitive_data_ack
            ):
                return True
        return False

    def log_audit_portal_access(self, entry: AuditPortalAccessLog) -> AuditPortalAccessLog:
        with self._lock:
            self._audit_access_logs.append(entry)
            return entry

    def append_audit_progress_history(self, email: str, payload: dict, *, keep_last: int = 60) -> None:
        from src.gateway.audit_progress import audit_progress_decision_count

        now = datetime.now(timezone.utc)
        incoming_count = audit_progress_decision_count(payload)
        with self._lock:
            per_email = [(i, e, p, t) for i, (e, p, t) in enumerate(self._audit_progress_history) if e == email]
            if per_email:
                _, _, last_payload, last_time = per_email[-1]
                if (
                    audit_progress_decision_count(last_payload) == incoming_count
                    and (now - last_time).total_seconds() < 15
                ):
                    return

            self._audit_progress_history.append((email, payload, now))
            per_email = [(i, e, p, t) for i, (e, p, t) in enumerate(self._audit_progress_history) if e == email]
            if len(per_email) <= keep_last:
                return

            # Solo podar instantáneas vacías; nunca borrar filas con decisiones.
            empty = [
                (i, e, p, t)
                for i, e, p, t in per_email
                if audit_progress_decision_count(p) <= 0
            ]
            drop = {i for i, *_ in empty[:-keep_last]}
            if drop:
                self._audit_progress_history = [
                    item for idx, item in enumerate(self._audit_progress_history) if idx not in drop
                ]

    def get_execution_plan(self, plan_id: str) -> ExecutionPlanRecord | None:
        return self._execution_plans.get(plan_id)

    def save_execution_plan(self, record: ExecutionPlanRecord) -> ExecutionPlanRecord:
        now = datetime.now(timezone.utc)
        with self._lock:
            existing = self._execution_plans.get(record.plan_id)
            if existing:
                existing.session_id = record.session_id
                existing.initiator_user_id = record.initiator_user_id
                existing.channel = record.channel
                existing.user_message = record.user_message
                existing.status = record.status
                existing.payload = record.payload
                existing.updated_at = now
                return existing
            record.created_at = now
            record.updated_at = now
            self._execution_plans[record.plan_id] = record
            return record

    def list_execution_plans(self, *, limit: int = 50) -> list[ExecutionPlanRecord]:
        with self._lock:
            items = sorted(
                self._execution_plans.values(),
                key=lambda r: r.updated_at,
                reverse=True,
            )
            return items[:limit]

    def execution_plan_stats(self) -> dict:
        from src.storage.models import aggregate_execution_plan_stats

        with self._lock:
            return aggregate_execution_plan_stats(list(self._execution_plans.values()))

    def clear_all_execution_plans(self) -> int:
        with self._lock:
            count = len(self._execution_plans)
            self._execution_plans.clear()
            return count

    # --- Config store ---
    def add_config_version(self, row: ConfigVersion) -> ConfigVersion:
        with self._lock:
            self._config_version_seq += 1
            stored = ConfigVersion(
                id=self._config_version_seq,
                kind=row.kind,
                key=row.key,
                version=row.version,
                content=row.content,
                checksum=row.checksum,
                author_email=row.author_email,
                note=row.note,
                created_at=row.created_at,
            )
            self._config_versions.append(stored)
            return stored

    def get_config_version(self, kind: str, key: str, version: int) -> ConfigVersion | None:
        with self._lock:
            for row in self._config_versions:
                if row.kind == kind and row.key == key and row.version == version:
                    return row
            return None

    def list_config_versions(self, kind: str, key: str, *, limit: int = 50) -> list[ConfigVersion]:
        with self._lock:
            rows = [r for r in self._config_versions if r.kind == kind and r.key == key]
            rows.sort(key=lambda r: r.version, reverse=True)
            return rows[:limit]

    def get_config_active(self, kind: str, key: str) -> ConfigActive | None:
        with self._lock:
            return self._config_active.get((kind, key))

    def upsert_config_active(self, row: ConfigActive) -> ConfigActive:
        with self._lock:
            self._config_active[(row.kind, row.key)] = row
            return row

    def delete_config_active(self, kind: str, key: str) -> bool:
        with self._lock:
            return self._config_active.pop((kind, key), None) is not None

    def delete_config_versions(self, kind: str, key: str) -> int:
        with self._lock:
            before = len(self._config_versions)
            self._config_versions = [
                r for r in self._config_versions if not (r.kind == kind and r.key == key)
            ]
            return before - len(self._config_versions)

    def list_config_active(self, *, kind: str | None = None) -> list[ConfigActive]:
        with self._lock:
            rows = list(self._config_active.values())
            if kind:
                rows = [r for r in rows if r.kind == kind]
            rows.sort(key=lambda r: (r.kind, r.key))
            return rows

    # --- Triple chat (Fase 1) ---
    def get_client_thread(self, thread_id: str) -> ClientThread | None:
        with self._lock:
            return self._client_threads.get(thread_id)

    def get_client_thread_by_cliente_session(self, cliente_session_id: str) -> ClientThread | None:
        with self._lock:
            for thread in self._client_threads.values():
                if thread.cliente_session_id == cliente_session_id:
                    return thread
            return None

    def get_client_thread_by_lawyer_session(self, lawyer_session_id: str) -> ClientThread | None:
        with self._lock:
            matches = [
                t
                for t in self._client_threads.values()
                if t.lawyer_session_id == lawyer_session_id
            ]
            if not matches:
                return None
            matches.sort(key=lambda t: t.updated_at, reverse=True)
            return matches[0]

    def save_client_thread(self, thread: ClientThread) -> ClientThread:
        with self._lock:
            self._client_threads[thread.thread_id] = thread
            return thread

    def add_client_message(self, message: ClientMessage) -> ClientMessage:
        with self._lock:
            self._client_messages.append(message)
            return message

    def list_client_messages(self, thread_id: str, *, limit: int = 200) -> list[ClientMessage]:
        with self._lock:
            rows = [m for m in self._client_messages if m.thread_id == thread_id]
            rows.sort(key=lambda m: m.created_at)
            return rows[:limit]

    def add_internal_transcript_entry(
        self, entry: InternalTranscriptEntry
    ) -> InternalTranscriptEntry:
        with self._lock:
            self._internal_transcript.append(entry)
            return entry

    def list_internal_transcript(
        self, session_id: str, *, limit: int = 100
    ) -> list[InternalTranscriptEntry]:
        with self._lock:
            rows = [e for e in self._internal_transcript if e.session_id == session_id]
            rows.sort(key=lambda e: e.created_at)
            return rows[:limit]

    def get_outbound_client_draft(self, draft_id: str) -> OutboundClientDraft | None:
        with self._lock:
            return self._outbound_client_drafts.get(draft_id)

    def save_outbound_client_draft(self, draft: OutboundClientDraft) -> OutboundClientDraft:
        with self._lock:
            self._outbound_client_drafts[draft.id] = draft
            return draft

    def list_outbound_client_drafts(
        self,
        *,
        status: str | None = None,
        thread_id: str | None = None,
        lawyer_session_id: str | None = None,
        limit: int = 100,
    ) -> list[OutboundClientDraft]:
        with self._lock:
            rows = list(self._outbound_client_drafts.values())
            if status:
                rows = [d for d in rows if d.status == status]
            if thread_id:
                rows = [d for d in rows if d.thread_id == thread_id]
            if lawyer_session_id:
                rows = [d for d in rows if d.lawyer_session_id == lawyer_session_id]
            rows.sort(key=lambda d: d.updated_at, reverse=True)
            return rows[:limit]

"""Trazas de flujo por sesión (Postgres o memoria según DATABASE_URL)."""

from __future__ import annotations

import time

from src.storage import get_repository
from src.storage.models import SessionTrace


class TraceStore:
    def add(self, session_id: str, trace: dict) -> None:
        payload = {"ts": time.time(), **trace}
        get_repository().add_session_trace(
            SessionTrace(
                session_id=session_id,
                trace_id=str(trace.get("trace_id") or ""),
                turn_index=int(trace.get("turn_index") or 0),
                payload=payload,
            )
        )

    def get(self, session_id: str, limit: int = 20) -> list[dict]:
        records = get_repository().list_session_traces(session_id, limit=limit)
        return [r.to_dict() for r in records]

    def latest(self, session_id: str) -> dict | None:
        records = get_repository().list_session_traces(session_id, limit=1)
        return records[-1].to_dict() if records else None


trace_store = TraceStore()

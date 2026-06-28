"""Registro en memoria para trazas de flujo por sesión."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TraceStore:
    _data: dict[str, list[dict]] = field(default_factory=dict)

    def add(self, session_id: str, trace: dict) -> None:
        payload = {"ts": time.time(), **trace}
        self._data.setdefault(session_id, []).append(payload)
        if len(self._data[session_id]) > 100:
            self._data[session_id] = self._data[session_id][-100:]

    def get(self, session_id: str, limit: int = 20) -> list[dict]:
        traces = self._data.get(session_id, [])
        return traces[-limit:]

    def latest(self, session_id: str) -> dict | None:
        traces = self._data.get(session_id, [])
        return traces[-1] if traces else None


trace_store = TraceStore()


"""Bus de eventos para ejecución de planes (SSE Fase 2)."""

from __future__ import annotations

import asyncio
import time
from typing import Any, AsyncIterator

PLAN_EVENT_TYPES = frozenset(
    {
        "execution_started",
        "heartbeat",
        "step_started",
        "step_io",
        "step_done",
        "plan_done",
        "plan_failed",
    }
)


class PlanEventBroker:
    """Broker in-process (un worker). Multi-instancia requeriría Redis en el futuro."""

    _instance: PlanEventBroker | None = None

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict[str, Any] | None]]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._seq: dict[str, int] = {}
        self._closed: set[str] = set()
        self._lock = asyncio.Lock()

    @classmethod
    def get(cls) -> PlanEventBroker:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_singleton_for_tests(cls) -> None:
        cls._instance = None

    async def reset_plan(self, plan_id: str) -> None:
        async with self._lock:
            self._closed.discard(plan_id)
            self._history.pop(plan_id, None)
            self._seq[plan_id] = 0

    async def seed_history(self, plan_id: str, events: list[dict[str, Any]]) -> None:
        """Carga eventos persistidos si el broker in-process aún no tiene historial."""
        if not events:
            return
        async with self._lock:
            if self._history.get(plan_id):
                return
            ordered = sorted(events, key=lambda e: int(e.get("seq", 0)))
            self._history[plan_id] = list(ordered)
            self._seq[plan_id] = max(int(e.get("seq", 0)) for e in ordered)
            if ordered and ordered[-1].get("event") in ("plan_done", "plan_failed"):
                self._closed.add(plan_id)

    def get_history(self, plan_id: str, *, after_seq: int = 0) -> list[dict[str, Any]]:
        return [e for e in self._history.get(plan_id, []) if int(e.get("seq", 0)) > after_seq]

    def is_terminal(self, plan_id: str) -> bool:
        history = self._history.get(plan_id, [])
        if not history:
            return plan_id in self._closed
        return history[-1].get("event") in ("plan_done", "plan_failed")

    async def publish(
        self,
        plan_id: str,
        event: str,
        payload: dict[str, Any] | None = None,
        *,
        step_id: str | None = None,
    ) -> dict[str, Any]:
        if event not in PLAN_EVENT_TYPES:
            raise ValueError(f"Evento de plan no soportado: {event}")
        async with self._lock:
            seq = self._seq.get(plan_id, 0) + 1
            self._seq[plan_id] = seq
            record: dict[str, Any] = {
                "event": event,
                "plan_id": plan_id,
                "seq": seq,
                "at_ms": int(time.time() * 1000),
                "step_id": step_id,
                "payload": payload or {},
            }
            self._history.setdefault(plan_id, []).append(record)
            queues = list(self._queues.get(plan_id, []))
        for queue in queues:
            try:
                queue.put_nowait(record)
            except asyncio.QueueFull:
                pass
        return record

    async def close(self, plan_id: str) -> None:
        async with self._lock:
            self._closed.add(plan_id)
            queues = list(self._queues.get(plan_id, []))
        for queue in queues:
            try:
                queue.put_nowait(None)
            except asyncio.QueueFull:
                pass

    async def subscribe(self, plan_id: str, *, after_seq: int = 0) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(maxsize=300)
        async with self._lock:
            self._queues.setdefault(plan_id, []).append(queue)
            backlog = [e for e in self._history.get(plan_id, []) if int(e.get("seq", 0)) > after_seq]
        for item in backlog:
            yield item
            if item.get("event") in ("plan_done", "plan_failed"):
                return
        if self.is_terminal(plan_id):
            return
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    if self.is_terminal(plan_id):
                        return
                    yield {
                        "event": "heartbeat",
                        "plan_id": plan_id,
                        "seq": 0,
                        "at_ms": int(time.time() * 1000),
                        "step_id": None,
                        "payload": {"message": "keepalive"},
                    }
                    continue
                if item is None:
                    return
                yield item
                if item.get("event") in ("plan_done", "plan_failed"):
                    return
        finally:
            async with self._lock:
                subs = self._queues.get(plan_id, [])
                if queue in subs:
                    subs.remove(queue)

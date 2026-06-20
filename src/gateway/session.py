"""Sesiones por canal/usuario."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field


@dataclass
class SessionStore:
    """Almacén en memoria; Redis opcional en producción."""

    _data: dict[str, list[dict]] = field(default_factory=dict)
    _redis: object | None = None

    def _key(self, channel: str, user_id: str) -> str:
        return f"{channel}:{user_id}"

    def append(self, channel: str, user_id: str, role: str, content: str) -> None:
        key = self._key(channel, user_id)
        self._data.setdefault(key, []).append(
            {"role": role, "content": content, "ts": time.time()}
        )
        if len(self._data[key]) > 20:
            self._data[key] = self._data[key][-20:]

    def history(self, channel: str, user_id: str) -> list[dict]:
        return self._data.get(self._key(channel, user_id), [])


session_store = SessionStore()

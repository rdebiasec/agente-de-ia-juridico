"""Sesiones de conversación (Postgres o memoria según DATABASE_URL)."""

from __future__ import annotations

from src.config import get_settings
from src.storage import get_repository


class SessionStore:
    """Historial multi-turno por canal/usuario, persistido en el repositorio."""

    def _key(self, channel: str, user_id: str) -> str:
        return f"{channel}:{user_id}"

    def append(self, channel: str, user_id: str, role: str, content: str) -> None:
        settings = get_settings()
        get_repository().append_chat_message(
            self._key(channel, user_id),
            channel=channel,
            user_id=user_id,
            role=role,
            content=content,
            max_messages=settings.session_max_messages,
        )

    def history(self, channel: str, user_id: str) -> list[dict]:
        session = get_repository().get_chat_session(self._key(channel, user_id))
        return list(session.messages) if session else []


session_store = SessionStore()

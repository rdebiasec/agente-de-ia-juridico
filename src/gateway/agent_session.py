"""Sesión del Agents SDK respaldada por el repositorio (Postgres o memoria)."""

from __future__ import annotations

from typing import Any

from agents.memory.session import SessionABC

from src.gateway.message_content import normalize_message_content, strip_runner_injected_context
from src.storage import get_repository


def _stored_content(role: str, content: Any) -> str:
    text = normalize_message_content(content)
    if role == "user":
        text = strip_runner_injected_context(text)
    return text.strip()


class RepositoryAgentSession(SessionABC):
    """Mantiene el historial de conversación para Runner.run(session=...)."""

    def __init__(self, session_id: str, *, channel: str = "web", user_id: str = ""):
        self.session_id = session_id
        self.channel = channel
        self.user_id = user_id
        self.session_settings = None

    def _to_input_item(self, msg: dict) -> dict[str, Any]:
        role = msg.get("role", "user")
        content = _stored_content(str(role), msg.get("content", ""))
        if role == "assistant":
            return {"role": "assistant", "content": content}
        return {"role": "user", "content": content}

    async def get_items(self, limit: int | None = None) -> list[Any]:
        repo = get_repository()
        session = repo.get_chat_session(self.session_id)
        if session is None:
            return []
        items = [self._to_input_item(m) for m in session.messages if m.get("content")]
        if limit is not None:
            return items[-limit:]
        return items

    async def add_items(self, items: list[Any]) -> None:
        repo = get_repository()
        from src.config import get_settings

        max_messages = get_settings().session_max_messages
        for item in items:
            if isinstance(item, dict):
                role = item.get("role") or "user"
                content = item.get("content") or ""
            else:
                role = getattr(item, "role", "user")
                content = getattr(item, "content", str(item))
            stored = _stored_content(str(role), content)
            if not stored:
                continue
            repo.append_chat_message(
                self.session_id,
                channel=self.channel,
                user_id=self.user_id,
                role=str(role),
                content=stored,
                max_messages=max_messages,
            )

    async def pop_item(self) -> Any | None:
        repo = get_repository()
        session = repo.get_chat_session(self.session_id)
        if session is None or not session.messages:
            return None
        last = session.messages.pop()
        repo.save_chat_session(session)
        return self._to_input_item(last)

    async def clear_session(self) -> None:
        repo = get_repository()
        session = repo.get_chat_session(self.session_id)
        if session is None:
            return
        session.messages = []
        repo.save_chat_session(session)


def reconcile_turn_messages(session_id: str, *, user_text: str, assistant_text: str) -> None:
    """Corrige el último par user/assistant tras Runner.run (RAG en input, dict en output)."""
    repo = get_repository()
    session = repo.get_chat_session(session_id)
    if not session or not session.messages:
        return
    user_clean = _stored_content("user", user_text)
    asst_clean = _stored_content("assistant", assistant_text)
    if session.messages[-1].get("role") == "assistant":
        session.messages[-1]["content"] = asst_clean
    for i in range(len(session.messages) - 1, -1, -1):
        if session.messages[i].get("role") == "user":
            session.messages[i]["content"] = user_clean
            break
    repo.save_chat_session(session)

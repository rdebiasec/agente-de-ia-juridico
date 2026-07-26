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


def _preview(text: str, limit: int = 160) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


def compact_session_items(
    items: list[Any],
    *,
    recent_messages: int,
    summary_max_chars: int,
) -> list[Any]:
    """Mantiene los últimos N mensajes y resume el resto (G2 session compact)."""
    if recent_messages <= 0 or len(items) <= recent_messages:
        return items
    older = items[:-recent_messages]
    recent = items[-recent_messages:]
    lines: list[str] = []
    for item in older:
        if isinstance(item, dict):
            role = str(item.get("role") or "item")
            content = _preview(str(item.get("content") or ""))
        else:
            role = str(getattr(item, "role", "item"))
            content = _preview(str(getattr(item, "content", item)))
        if content:
            lines.append(f"- {role}: {content}")
    summary = "\n".join(lines)
    if len(summary) > summary_max_chars:
        summary = summary[: summary_max_chars - 3] + "..."
    summary_item = {
        "role": "user",
        "content": (
            "[Resumen de turnos previos de la sesión — contexto compactado]\n"
            f"{summary}"
        ),
    }
    return [summary_item, *recent]


class RepositoryAgentSession(SessionABC):
    """Mantiene el historial de conversación para Runner.run(session=...)."""

    def __init__(self, session_id: str, *, channel: str = "web", user_id: str = ""):
        self.session_id = session_id
        self.channel = channel
        self.user_id = user_id
        self.session_settings = None
        self.last_compaction: dict[str, int] | None = None

    def _to_input_item(self, msg: dict) -> dict[str, Any]:
        role = msg.get("role", "user")
        content = _stored_content(str(role), msg.get("content", ""))
        if role == "assistant":
            return {"role": "assistant", "content": content}
        return {"role": "user", "content": content}

    async def get_items(self, limit: int | None = None) -> list[Any]:
        from src.config import get_settings

        repo = get_repository()
        session = repo.get_chat_session(self.session_id)
        if session is None:
            self.last_compaction = {"raw": 0, "sent": 0, "compacted": 0}
            return []
        items = [self._to_input_item(m) for m in session.messages if m.get("content")]
        if limit is not None:
            items = items[-limit:]
        settings = get_settings()
        raw_count = len(items)
        compacted = compact_session_items(
            items,
            recent_messages=settings.session_recent_messages,
            summary_max_chars=settings.session_summary_max_chars,
        )
        self.last_compaction = {
            "raw": raw_count,
            "sent": len(compacted),
            "compacted": 1 if len(compacted) < raw_count else 0,
        }
        return compacted

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
            # No persistir el resumen sintético de compactación.
            if stored.startswith("[Resumen de turnos previos"):
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

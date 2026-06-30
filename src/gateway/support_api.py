"""API de consola de soporte — operaciones y trazas OpenAI."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.auth.deps import require_web_session
from src.storage import get_repository

router = APIRouter(prefix="/support", tags=["support"], dependencies=[Depends(require_web_session)])


def _summarize_trace(record) -> dict:
    payload = record.payload or {}
    completion = payload.get("completion") or {}
    summary = completion.get("summary") or {}
    calls = completion.get("calls") or []
    return {
        "record_id": record.id,
        "session_id": record.session_id,
        "trace_id": payload.get("trace_id") or record.trace_id,
        "turn_index": record.turn_index,
        "created_at": record.created_at.isoformat(),
        "channel": payload.get("channel", "web"),
        "input_summary": payload.get("input_summary", ""),
        "route": payload.get("route") or payload.get("sent_to_agent") or "",
        "sent_to_agent": payload.get("sent_to_agent", ""),
        "skill_kan": payload.get("skill_kan", ""),
        "blocked": bool(payload.get("blocked")),
        "pending_review": bool(payload.get("human_review_required")),
        "span_count": payload.get("span_count") or len(payload.get("spans") or []),
        "completion_calls": summary.get("calls") or len(calls),
        "tokens_total": summary.get("total_tokens") or 0,
        "response_ids": [c.get("response_id") for c in calls if c.get("response_id")],
    }


@router.get("/operations")
async def list_operations(limit: int = Query(default=40, ge=1, le=100)):
    """Operaciones recientes con resumen para la consola de soporte."""
    repo = get_repository()
    traces = repo.list_recent_session_traces(limit=limit)
    return {"operations": [_summarize_trace(t) for t in traces]}


@router.get("/sessions")
async def list_sessions(limit: int = Query(default=25, ge=1, le=100)):
    """Sesiones de chat recientes."""
    repo = get_repository()
    sessions = repo.list_chat_sessions(limit=limit)
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "channel": s.channel,
                "user_id": s.user_id,
                "message_count": len(s.messages),
                "updated_at": s.updated_at.isoformat(),
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
    }


@router.get("/operations/{session_id}")
async def session_operations(session_id: str, limit: int = Query(default=40, ge=1, le=100)):
    raw = (session_id or "").strip()
    if not raw or len(raw) > 120:
        raise HTTPException(status_code=400, detail="session_id inválido.")
    repo = get_repository()
    traces = repo.list_session_traces(raw, limit=limit)
    chat = repo.get_chat_session(raw)
    exp = repo.get_expediente(raw)
    return {
        "session_id": raw,
        "message_count": len(chat.messages) if chat else 0,
        "expediente": exp.to_dict() if exp else None,
        "operations": [_summarize_trace(t) for t in traces],
        "traces": [t.to_dict() for t in traces],
    }

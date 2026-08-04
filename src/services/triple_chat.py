"""Triple chat — hilos cliente, drafts outbound HITL y transcript interno (Fase 1)."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from src.storage import get_repository
from src.storage.models import (
    MSG_VIS_CLIENT,
    MSG_VIS_INTERNAL,
    MSG_VIS_PENDING,
    OUTBOUND_APPROVED,
    OUTBOUND_PROPOSED,
    OUTBOUND_REJECTED,
    OUTBOUND_SENT,
    ClientMessage,
    ClientThread,
    Expediente,
    InternalTranscriptEntry,
    OutboundClientDraft,
)

_SESSION_SAFE = re.compile(r"^[a-zA-Z0-9_.:@-]{3,120}$")


class TripleChatError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_cliente_session(subject: str) -> str:
    raw = (subject or "").strip()
    if not raw:
        raise TripleChatError("cliente_session_id / subject requerido.")
    if raw.startswith("cliente:"):
        sid = raw
    else:
        sid = f"cliente:{raw}"
    if not _SESSION_SAFE.match(sid):
        raise TripleChatError("Identificador de sesión cliente inválido.")
    return sid


def normalize_lawyer_session(session_id: str | None, *, fallback_user: str = "abogado") -> str:
    raw = (session_id or "").strip()
    if not raw:
        raw = f"web:{fallback_user}"
    if not raw.startswith("web:") and ":" not in raw:
        raw = f"web:{raw}"
    if not _SESSION_SAFE.match(raw):
        raise TripleChatError("lawyer_session_id inválido.")
    return raw


def _stub_gerente_proposal(inbound: str) -> str:
    """Compat: delega al borrador contextual."""
    from src.services.cliente_reply_draft import contextual_gerente_draft

    return contextual_gerente_draft(inbound, lawyer_session_id="web:abogado")


AUTH_BY_LAWYER_IMPERSONATION = "lawyer_impersonation"


def _welcome_text(*, display_name: str) -> str:
    """Saludo breve del Coordinador (tono víctima; sin listar especialidades)."""
    name = (display_name or "").strip() or "usted"
    greeting = "Buenos días"
    try:
        from zoneinfo import ZoneInfo

        hour = datetime.now(ZoneInfo("America/Bogota")).hour
        if 12 <= hour < 19:
            greeting = "Buenas tardes"
        elif hour >= 19 or hour < 5:
            greeting = "Buenas noches"
    except Exception:
        pass
    return (
        f"{greeting}, {name}. Soy el Coordinador del Caso de Lexiatek. "
        "Puede contarme su situación con tranquilidad; un abogado del despacho "
        "revisará cada respuesta antes de enviársela."
    )


def start_cliente_session(
    *,
    nombre: str,
    consent_1581: bool,
    cliente_subject: str | None = None,
    lawyer_session_id: str | None = None,
    telefono: str | None = None,
    email: str | None = None,
) -> dict:
    """
    Identidad v1 + consentimiento 1581 en servidor.
    Crea/actualiza hilo, cookie subject y mensaje de bienvenida del Coordinador.
    """
    if not consent_1581:
        raise TripleChatError(
            "Debe autorizar el tratamiento de datos (Ley 1581) para comenzar."
        )
    display = (nombre or "").strip()
    if len(display) < 2:
        raise TripleChatError("nombre requerido (mínimo 2 caracteres).")
    if len(display) > 120:
        raise TripleChatError("nombre demasiado largo.")

    from src.auth.cliente_session import new_cliente_subject_id

    bare = (cliente_subject or "").strip() or new_cliente_subject_id()
    if bare.startswith("cliente:"):
        bare = bare.split(":", 1)[-1]
    cliente_sid = normalize_cliente_session(bare)
    lawyer_sid = normalize_lawyer_session(lawyer_session_id)

    thread = get_or_create_thread(
        cliente_session_id=cliente_sid,
        lawyer_session_id=lawyer_sid,
        subject_label=display,
    )
    repo = get_repository()
    meta = dict(thread.meta or {})
    consent_at = _now().isoformat()
    meta.update(
        {
            "client_display_name": display,
            "consent_at": consent_at,
            "consent_1581": True,
        }
    )
    phone = (telefono or "").strip()
    mail = (email or "").strip()
    if phone:
        meta["phone"] = phone[:40]
    if mail:
        meta["email"] = mail[:120]
    thread.meta = meta
    thread.subject_label = display
    thread.updated_at = _now()
    thread = repo.save_client_thread(thread)

    welcome_id = None
    if not meta.get("welcome_sent"):
        welcome = ClientMessage(
            thread_id=thread.thread_id,
            role="gerente",
            content=_welcome_text(display_name=display),
            visibility=MSG_VIS_CLIENT,
            meta={"authored_by": "system_welcome"},
        )
        welcome = repo.add_client_message(welcome)
        welcome_id = welcome.id
        meta["welcome_sent"] = True
        thread.meta = meta
        thread.updated_at = _now()
        thread = repo.save_client_thread(thread)

    return {
        "ok": True,
        "started": True,
        "thread_id": thread.thread_id,
        "cliente_session_id": cliente_sid,
        "lawyer_session_id": lawyer_sid,
        "client_display_name": display,
        "consent_at": consent_at,
        "welcome_message_id": welcome_id,
        "subject_label": thread.subject_label,
    }


def enqueue_client_message(
    *,
    message: str,
    cliente_subject: str,
    lawyer_session_id: str | None = None,
    subject_label: str = "",
    authored_by: str | None = None,
    lawyer_actor_id: str | None = None,
) -> dict:
    """
    Recibe mensaje de la víctima (o impersonación del despacho), encola propuesta HITL.
    No publica respuesta del Gerente al cliente.
    """
    text = (message or "").strip()
    if not text:
        raise TripleChatError("message vacío.")
    if len(text) > 8000:
        raise TripleChatError("message demasiado largo.")

    cliente_sid = normalize_cliente_session(cliente_subject)
    lawyer_sid = normalize_lawyer_session(lawyer_session_id)
    thread = get_or_create_thread(
        cliente_session_id=cliente_sid,
        lawyer_session_id=lawyer_sid,
        subject_label=subject_label,
    )

    # Consentimiento 1581 obligatorio en canal consumidor (no en impersonación desk).
    is_impersonation = (authored_by or "").strip() == AUTH_BY_LAWYER_IMPERSONATION
    if not is_impersonation and not (thread.meta or {}).get("consent_1581"):
        raise TripleChatError(
            "Debe completar el inicio de consulta y autorizar el tratamiento de datos (Ley 1581)."
        )

    inbound_meta: dict = {}
    if authored_by:
        inbound_meta["authored_by"] = authored_by.strip()
    if lawyer_actor_id:
        inbound_meta["lawyer_actor_id"] = str(lawyer_actor_id).strip()[:120]

    repo = get_repository()
    inbound = ClientMessage(
        thread_id=thread.thread_id,
        role="cliente",
        content=text,
        visibility=MSG_VIS_CLIENT,
        meta=inbound_meta,
    )
    inbound = repo.add_client_message(inbound)

    from src.services.cliente_reply_draft import build_outbound_proposal

    proposed, quality_flags = build_outbound_proposal(
        text, lawyer_session_id=lawyer_sid
    )

    draft = OutboundClientDraft(
        thread_id=thread.thread_id,
        lawyer_session_id=lawyer_sid,
        cliente_session_id=cliente_sid,
        inbound_message_id=inbound.id,
        proposed_text=proposed,
        status=OUTBOUND_PROPOSED,
        comentario=(
            "Calidad: " + ", ".join(quality_flags) if quality_flags else None
        ),
    )
    draft = repo.save_outbound_client_draft(draft)

    # Placeholder interno (no visible al cliente) ligado al draft.
    pending = ClientMessage(
        thread_id=thread.thread_id,
        role="gerente",
        content=draft.proposed_text,
        visibility=MSG_VIS_PENDING,
        outbound_draft_id=draft.id,
        meta={"draft_status": "pending_hitl"},
    )
    repo.add_client_message(pending)

    thread.updated_at = _now()
    repo.save_client_thread(thread)

    if is_impersonation:
        try:
            from src.services.bitacora import append_entries

            actor = (lawyer_actor_id or "abogado").strip() or "abogado"
            append_entries(
                lawyer_sid,
                [
                    {
                        "autor": actor,
                        "tipo": "nota",
                        "resumen": (
                            "Mensaje escrito como la víctima (impersonación del despacho) "
                            f"en canal cliente; draft HITL {draft.id}."
                        ),
                        "fuentes": ["canal_victima", "lawyer_impersonation"],
                        "confidencialidad": "sensible",
                    }
                ],
            )
        except Exception:
            import logging

            logging.getLogger(__name__).exception(
                "Bitácora impersonación omitida session=%s", lawyer_sid
            )

    return {
        "status": "en_revision",
        "status_label": "En revisión del despacho",
        "thread_id": thread.thread_id,
        "draft_id": draft.id,
        "inbound_message_id": inbound.id,
        "client_ack": (
            "Su mensaje fue recibido. El despacho lo está revisando; "
            "le responderá el Coordinador del Caso cuando el abogado apruebe."
        ),
        "cliente_session_id": cliente_sid,
        "lawyer_session_id": lawyer_sid,
        "quality_flags": quality_flags,
        "authored_by": inbound_meta.get("authored_by"),
    }


def link_expediente_sessions(
    *,
    lawyer_session_id: str,
    cliente_session_id: str,
) -> Expediente:
    """Asegura expediente del desk con vínculo al canal cliente."""
    repo = get_repository()
    exp = repo.get_expediente(lawyer_session_id) or Expediente(session_id=lawyer_session_id)
    exp.lawyer_session_id = lawyer_session_id
    exp.cliente_session_id = cliente_session_id
    exp.actualizado_en = _now().timestamp()
    return repo.save_expediente(exp)


def get_or_create_thread(
    *,
    cliente_session_id: str,
    lawyer_session_id: str,
    subject_label: str = "",
) -> ClientThread:
    repo = get_repository()
    existing = repo.get_client_thread_by_cliente_session(cliente_session_id)
    if existing:
        if lawyer_session_id and existing.lawyer_session_id != lawyer_session_id:
            existing.lawyer_session_id = lawyer_session_id
            existing.expediente_session_id = lawyer_session_id
            existing.updated_at = _now()
            existing = repo.save_client_thread(existing)
            link_expediente_sessions(
                lawyer_session_id=lawyer_session_id,
                cliente_session_id=cliente_session_id,
            )
        return existing

    thread = ClientThread(
        cliente_session_id=cliente_session_id,
        lawyer_session_id=lawyer_session_id,
        expediente_session_id=lawyer_session_id,
        subject_label=subject_label or cliente_session_id,
    )
    saved = repo.save_client_thread(thread)
    link_expediente_sessions(
        lawyer_session_id=lawyer_session_id,
        cliente_session_id=cliente_session_id,
    )
    return saved


def _cliente_public_message(msg: ClientMessage) -> dict:
    """Vista víctima: sin meta interna ni authored_by del despacho."""
    return {
        "id": msg.id,
        "thread_id": msg.thread_id,
        "role": msg.role,
        "content": msg.content,
        "visibility": msg.visibility,
        "created_at": msg.created_at.isoformat(),
    }


def list_cliente_visible_messages(cliente_subject: str) -> dict:
    cliente_sid = normalize_cliente_session(cliente_subject)
    repo = get_repository()
    thread = repo.get_client_thread_by_cliente_session(cliente_sid)
    if not thread:
        return {
            "thread_id": None,
            "messages": [],
            "status": "sin_hilo",
            "status_label": "Sin conversación aún",
            "started": False,
        }
    msgs = [
        _cliente_public_message(m)
        for m in repo.list_client_messages(thread.thread_id)
        if m.visibility == MSG_VIS_CLIENT
    ]
    pending = [
        d
        for d in repo.list_outbound_client_drafts(thread_id=thread.thread_id)
        if d.status == OUTBOUND_PROPOSED
    ]
    has_gerente = any(m.get("role") == "gerente" for m in msgs)
    if pending:
        status, label = "en_revision", "En revisión del despacho"
    elif has_gerente:
        status, label = "respuesta_lista", "Respuesta del Coordinador disponible"
    else:
        status, label = "al_dia", "Listo para su mensaje"
    meta = dict(thread.meta or {})
    return {
        "thread_id": thread.thread_id,
        "messages": msgs,
        "status": status,
        "status_label": label,
        "pending_drafts": len(pending),
        "lawyer_session_id": thread.lawyer_session_id,
        "subject_label": thread.subject_label,
        "started": bool(meta.get("consent_1581")),
        "client_display_name": meta.get("client_display_name") or thread.subject_label,
        "consent_at": meta.get("consent_at"),
    }


def list_lawyer_cliente_thread(lawyer_session_id: str) -> dict:
    """
    Hilo canal víctima para el desk: mensajes cliente + gerente visible +
    pending_hitl como «borrador en revisión». No expone junta interna.
    """
    from src.agents.pii import mask_pii

    lawyer_sid = normalize_lawyer_session(lawyer_session_id)
    repo = get_repository()
    thread = repo.get_client_thread_by_lawyer_session(lawyer_sid)
    if not thread:
        # Fallback: expediente → cliente_session_id
        exp = repo.get_expediente(lawyer_sid)
        if exp and getattr(exp, "cliente_session_id", None):
            thread = repo.get_client_thread_by_cliente_session(exp.cliente_session_id)
    if not thread:
        return {
            "thread_id": None,
            "messages": [],
            "lawyer_session_id": lawyer_sid,
            "webchat_url": f"/cliente?caso={lawyer_sid}",
            "client_display_name": None,
            "started": False,
        }

    enriched = []
    for m in repo.list_client_messages(thread.thread_id):
        if m.visibility == MSG_VIS_INTERNAL:
            continue
        data = m.to_dict()
        data["content"] = mask_pii(data.get("content") or "")
        authored = (m.meta or {}).get("authored_by")
        if m.role == "cliente" and authored == AUTH_BY_LAWYER_IMPERSONATION:
            data["badge"] = "escrito_por_despacho"
            data["badge_label"] = "Escrito por el despacho"
        elif m.role == "cliente":
            data["badge"] = "victima"
            data["badge_label"] = "Víctima"
        elif m.visibility == MSG_VIS_PENDING:
            data["badge"] = "borrador_pendiente"
            data["badge_label"] = "Borrador pendiente"
            data["desk_label"] = "borrador en revisión"
        elif m.role == "gerente":
            data["badge"] = "coordinador_enviado"
            data["badge_label"] = "Coordinador (enviado)"
        else:
            data["badge"] = m.role
            data["badge_label"] = m.role
        # No filtrar meta authored_by al desk; sí omitir datos de junta (no hay).
        enriched.append(data)

    meta = dict(thread.meta or {})
    return {
        "thread_id": thread.thread_id,
        "messages": enriched,
        "lawyer_session_id": thread.lawyer_session_id,
        "cliente_session_id": thread.cliente_session_id,
        "webchat_url": f"/cliente?caso={thread.lawyer_session_id}",
        "client_display_name": meta.get("client_display_name") or thread.subject_label,
        "consent_at": meta.get("consent_at"),
        "started": bool(meta.get("consent_1581")),
        "subject_label": thread.subject_label,
        "meta": {
            "client_display_name": meta.get("client_display_name"),
            "consent_at": meta.get("consent_at"),
            "consent_1581": meta.get("consent_1581"),
        },
    }


def enqueue_lawyer_as_client(
    *,
    message: str,
    lawyer_session_id: str,
    lawyer_actor_id: str | None = None,
) -> dict:
    """Impersonación desk → mismo hilo role=cliente + HITL outbound."""
    lawyer_sid = normalize_lawyer_session(lawyer_session_id)
    repo = get_repository()
    thread = repo.get_client_thread_by_lawyer_session(lawyer_sid)
    if not thread:
        exp = repo.get_expediente(lawyer_sid)
        if exp and getattr(exp, "cliente_session_id", None):
            thread = repo.get_client_thread_by_cliente_session(exp.cliente_session_id)
    if not thread:
        # Crear hilo placeholder ligado al caso para que el abogado pueda iniciar.
        from src.auth.cliente_session import new_cliente_subject_id

        cliente_sid = normalize_cliente_session(new_cliente_subject_id())
        thread = get_or_create_thread(
            cliente_session_id=cliente_sid,
            lawyer_session_id=lawyer_sid,
            subject_label="Canal víctima (despacho)",
        )
    return enqueue_client_message(
        message=message,
        cliente_subject=thread.cliente_session_id,
        lawyer_session_id=lawyer_sid,
        subject_label=thread.subject_label or "",
        authored_by=AUTH_BY_LAWYER_IMPERSONATION,
        lawyer_actor_id=lawyer_actor_id,
    )


def _quality_flags_from_comentario(comentario: str | None) -> list[str]:
    raw = (comentario or "").strip()
    if not raw.lower().startswith("calidad:"):
        return []
    body = raw.split(":", 1)[1].strip()
    return [p.strip() for p in body.split(",") if p.strip()]


def _case_label_for_draft(draft: OutboundClientDraft) -> str:
    thread = get_repository().get_client_thread(draft.thread_id)
    if thread and (thread.subject_label or "").strip():
        return thread.subject_label.strip()
    sid = (draft.lawyer_session_id or "").strip()
    if sid.startswith("web:"):
        sid = sid[4:]
    short = sid[-8:] if len(sid) > 8 else sid
    return f"Caso {short or 'sin etiqueta'}"


def list_cliente_inbox(*, status: str | None = OUTBOUND_PROPOSED) -> dict:
    repo = get_repository()
    drafts = repo.list_outbound_client_drafts(status=status)
    enriched = []
    for d in drafts:
        row = d.to_dict()
        flags = _quality_flags_from_comentario(d.comentario)
        row["quality_flags"] = flags
        row["needs_quality_review"] = bool(flags)
        row["case_label"] = _case_label_for_draft(d)
        enriched.append(row)
    return {"drafts": enriched, "pending_count": len(enriched)}


def get_outbound_draft(draft_id: str) -> OutboundClientDraft:
    draft = get_repository().get_outbound_client_draft(draft_id)
    if draft is None:
        raise TripleChatError("Borrador outbound no encontrado.")
    return draft


def approve_outbound_draft(
    draft_id: str,
    *,
    revisor: str = "abogado",
    comentario: str | None = None,
    edited_text: str | None = None,
) -> dict:
    repo = get_repository()
    draft = get_outbound_draft(draft_id)
    if draft.status not in {OUTBOUND_PROPOSED}:
        raise TripleChatError(f"Estado inválido para aprobar: {draft.status}")

    final = (edited_text if edited_text is not None else draft.proposed_text).strip()
    if not final:
        raise TripleChatError("Texto final vacío.")

    draft.final_text = final
    draft.status = OUTBOUND_APPROVED
    draft.revisor = revisor
    draft.comentario = comentario
    draft.updated_at = _now()
    draft = repo.save_outbound_client_draft(draft)

    # Publicar al hilo cliente como visible.
    visible = ClientMessage(
        thread_id=draft.thread_id,
        role="gerente",
        content=final,
        visibility=MSG_VIS_CLIENT,
        outbound_draft_id=draft.id,
    )
    visible = repo.add_client_message(visible)

    draft.status = OUTBOUND_SENT
    draft.updated_at = _now()
    draft = repo.save_outbound_client_draft(draft)

    thread = repo.get_client_thread(draft.thread_id)
    if thread:
        thread.updated_at = _now()
        repo.save_client_thread(thread)

    return {"ok": True, "draft": draft.to_dict(), "published_message": visible.to_dict()}


def edit_outbound_draft(
    draft_id: str,
    *,
    contenido: str,
    revisor: str = "abogado",
    comentario: str | None = None,
) -> dict:
    """Guarda edición del texto propuesto sin publicar aún."""
    repo = get_repository()
    draft = get_outbound_draft(draft_id)
    if draft.status != OUTBOUND_PROPOSED:
        raise TripleChatError(f"Estado inválido para editar: {draft.status}")
    text = (contenido or "").strip()
    if not text:
        raise TripleChatError("contenido vacío.")
    draft.proposed_text = text
    draft.revisor = revisor
    draft.comentario = comentario
    draft.updated_at = _now()
    draft = repo.save_outbound_client_draft(draft)
    return {"ok": True, "draft": draft.to_dict()}


def reject_outbound_draft(
    draft_id: str,
    *,
    revisor: str = "abogado",
    comentario: str,
) -> dict:
    if not (comentario or "").strip():
        raise TripleChatError("comentario requerido al rechazar.")
    repo = get_repository()
    draft = get_outbound_draft(draft_id)
    if draft.status != OUTBOUND_PROPOSED:
        raise TripleChatError(f"Estado inválido para rechazar: {draft.status}")
    draft.status = OUTBOUND_REJECTED
    draft.revisor = revisor
    draft.comentario = comentario.strip()
    draft.updated_at = _now()
    draft = repo.save_outbound_client_draft(draft)
    return {"ok": True, "draft": draft.to_dict()}


KIND_DESK_LABELS = {
    "consult": "Consulta",
    "findings": "Hallazgos",
    "synthesize": "Síntesis",
    "escalate": "Escalamiento",
}


def _mask_clip(text: str, *, max_chars: int = 2400) -> str:
    from src.agents.pii import mask_pii

    normalized = " ".join((text or "").split())
    masked = mask_pii(normalized)
    if len(masked) <= max_chars:
        return masked
    return f"{masked[: max_chars - 3]}..."


def append_internal_transcript(
    *,
    session_id: str,
    from_actor: str,
    to_actor: str,
    pedido: str = "",
    respuesta: str = "",
    turn_ref: str | None = None,
    kind: str | None = None,
    ronda: int | None = None,
) -> InternalTranscriptEntry:
    entry = InternalTranscriptEntry(
        session_id=session_id,
        from_actor=from_actor,
        to_actor=to_actor,
        pedido=_mask_clip(pedido),
        respuesta=_mask_clip(respuesta),
        turn_ref=turn_ref,
        kind=(kind or "").strip() or None,
        ronda=int(ronda) if ronda else None,
    )
    return get_repository().add_internal_transcript_entry(entry)


def list_internal_transcript(session_id: str, *, limit: int = 100) -> dict:
    sid = (session_id or "").strip()
    if not sid:
        raise TripleChatError("session_id requerido.")
    from src.agents.agent_ids import JUNTA_ALTO_RIESGO_IDS, resolve_agent_id
    from src.agents.pii import mask_pii

    entries = get_repository().list_internal_transcript(sid, limit=limit)
    enriched = []
    for e in entries:
        data = e.to_dict()
        # Defensa en profundidad: re-mask al listar (filas históricas).
        data["pedido"] = mask_pii(data.get("pedido") or "")
        data["respuesta"] = mask_pii(data.get("respuesta") or "")
        data["from_label"] = _actor_label(e.from_actor, short=True)
        data["to_label"] = _actor_label(e.to_actor, short=True)
        data["from_label_full"] = _actor_label(e.from_actor, short=False)
        data["to_label_full"] = _actor_label(e.to_actor, short=False)
        data["kind_label"] = KIND_DESK_LABELS.get((e.kind or "").strip(), "")
        data["trace_id"] = e.turn_ref
        spec_id = ""
        if (e.to_actor or "").startswith("especialista:"):
            spec_id = resolve_agent_id(e.to_actor.split(":", 1)[1])
        data["specialist_id"] = spec_id
        data["alto_riesgo"] = spec_id in JUNTA_ALTO_RIESGO_IDS
        enriched.append(data)
    return {"session_id": sid, "entries": enriched}


def _actor_label(actor: str, *, short: bool = False) -> str:
    from src.agents.agent_ids import (
        AGENT_DESK_SHORT_LABELS,
        AGENT_DISPLAY_LABELS,
        LEGACY_AGENT_ALIASES,
        agent_desk_short_label,
        resolve_agent_id,
    )

    raw = (actor or "").strip()
    if raw in LEGACY_AGENT_ALIASES or resolve_agent_id(raw) == "coordinador_caso":
        if raw in {
            "gerente",
            "gerente_caso",
            "coordinador_expediente_penal",
            "coordinador_caso",
        }:
            if short:
                return AGENT_DESK_SHORT_LABELS["coordinador_caso"]
            return AGENT_DISPLAY_LABELS["coordinador_caso"]
    if raw.startswith("especialista:"):
        agent_id = resolve_agent_id(raw.split(":", 1)[1])
        if short:
            label = agent_desk_short_label(agent_id)
            if label:
                return label
        if agent_id in AGENT_DISPLAY_LABELS:
            return AGENT_DISPLAY_LABELS[agent_id]
        try:
            from src.services.bitacora import area_label

            return area_label(agent_id)
        except Exception:
            return agent_id
    canonical = resolve_agent_id(raw)
    if short:
        short_label = agent_desk_short_label(canonical)
        if short_label:
            return short_label
    if canonical in AGENT_DISPLAY_LABELS:
        return AGENT_DISPLAY_LABELS[canonical]
    try:
        from src.services.bitacora import area_label

        return area_label(canonical)
    except Exception:
        return raw or "equipo"


def record_specialist_exchange(
    *,
    session_id: str,
    specialist_id: str,
    pedido: str = "",
    respuesta: str = "",
    turn_ref: str | None = None,
    kind: str | None = "findings",
    ronda: int | None = None,
    max_chars: int = 2400,
) -> InternalTranscriptEntry | None:
    """Best-effort: persiste un turno Coordinador↔especialista para Junta del caso."""
    sid = (session_id or "").strip()
    spec = (specialist_id or "").strip()
    if not sid or not spec:
        return None

    try:
        clipped_pedido = _mask_clip(pedido, max_chars=max_chars)
        clipped_respuesta = _mask_clip(respuesta, max_chars=max_chars)
        entry = InternalTranscriptEntry(
            session_id=sid,
            from_actor="gerente",
            to_actor=f"especialista:{spec}",
            pedido=clipped_pedido or f"Consulta al área {spec}",
            respuesta=clipped_respuesta,
            turn_ref=turn_ref,
            kind=(kind or "findings").strip() or "findings",
            ronda=int(ronda) if ronda else None,
        )
        return get_repository().add_internal_transcript_entry(entry)
    except Exception:
        import logging

        logging.getLogger(__name__).exception(
            "No se pudo registrar transcript interno session=%s specialist=%s",
            sid,
            spec,
        )
        return None

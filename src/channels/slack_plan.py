"""Flujo de plan de ejecución para Slack (Fase 2 — sprint B)."""

from __future__ import annotations

import logging
import re

from src.agents.planner import approve_plan, create_execution_plan, reject_plan
from src.agents.plan_executor import schedule_execute_async, wait_for_plan_completion
from src.agents.skill_catalog import agent_display_name
from src.gateway.trace import trace_store
from src.storage import get_repository

logger = logging.getLogger(__name__)

_EXECUTE_RE = re.compile(r"^\s*(ejecutar|aprobar|si|s[ií]|ok|run)\s*$", re.I)

# Caché en proceso: thread_ts (o dm) -> plan_id. Fuente de verdad = repositorio.
_pending_plans: dict[str, str] = {}


def _thread_key(thread_ts: str | None, user_id: str) -> str:
    return thread_ts or f"dm:{user_id}"


def _session_id(user_id: str) -> str:
    return f"slack:{user_id}"


def _attach_slack_thread_key(plan_id: str, thread_key: str) -> None:
    repo = get_repository()
    record = repo.get_execution_plan(plan_id)
    if not record:
        return
    payload = dict(record.payload or {})
    payload["slack_thread_key"] = thread_key
    record.payload = payload
    repo.save_execution_plan(record)


def _find_pending_plan_id(thread_key: str, user_id: str) -> str | None:
    """Resuelve plan pendiente: caché RAM, luego repositorio (sobrevive redeploy)."""
    cached = _pending_plans.get(thread_key)
    if cached:
        record = get_repository().get_execution_plan(cached)
        if record and record.status == "pending_approval":
            return cached
        _pending_plans.pop(thread_key, None)

    session_id = _session_id(user_id)
    match_thread: str | None = None
    match_session: str | None = None
    for record in get_repository().list_execution_plans(limit=80):
        if record.status != "pending_approval":
            continue
        if record.session_id != session_id and record.channel != "slack":
            continue
        if record.session_id != session_id:
            continue
        payload = record.payload or {}
        if payload.get("slack_thread_key") == thread_key:
            match_thread = record.plan_id
            break
        if match_session is None:
            match_session = record.plan_id

    plan_id = match_thread or match_session
    if plan_id:
        _pending_plans[thread_key] = plan_id
    return plan_id


def _clear_pending(thread_key: str, plan_id: str | None = None) -> None:
    _pending_plans.pop(thread_key, None)
    if plan_id and plan_id in _pending_plans.values():
        for k, v in list(_pending_plans.items()):
            if v == plan_id:
                _pending_plans.pop(k, None)


def _format_plan_message(plan_dict: dict) -> str:
    lines = [
        "*Plan de ejecución propuesto*",
        f"*Objetivo:* {plan_dict.get('objective', '')}",
        "",
    ]
    for step in plan_dict.get("steps") or []:
        lines.append(
            f"{step.get('order')}. *{step.get('title')}* — {agent_display_name(step.get('agent_id', ''))}"
        )
        lines.append(f"   _{step.get('user_summary', '')}_")
    lines.extend(
        [
            "",
            "Responda *EJECUTAR* en este hilo para aprobar y correr el plan paso a paso.",
            "Responda *CAMBIOS: motivo* para solicitar otro plan.",
        ]
    )
    return "\n".join(lines)


async def handle_slack_plan_message(
    *,
    text: str,
    user_id: str,
    say,
    thread_ts: str | None,
) -> bool:
    """Maneja mensajes con flujo de plan. Retorna True si consumió el mensaje."""
    key = _thread_key(thread_ts, user_id)
    stripped = (text or "").strip()

    if stripped.upper().startswith("CAMBIOS:"):
        reason = stripped.split(":", 1)[-1].strip()
        plan_id = _find_pending_plan_id(key, user_id)
        if plan_id:
            reject_plan(plan_id, user_id, reason=reason)
        _clear_pending(key, plan_id)
        await say(
            "Entendido. Envíe una nueva consulta y generaré otro plan.",
            thread_ts=thread_ts,
        )
        return True

    if _EXECUTE_RE.match(stripped):
        plan_id = _find_pending_plan_id(key, user_id)
        if not plan_id:
            await say("No hay un plan pendiente en este hilo.", thread_ts=thread_ts)
            return True

        plan, err = approve_plan(plan_id, user_id)
        if err:
            await say(f"No pude aprobar el plan: {err}", thread_ts=thread_ts)
            return True

        await say("Plan aprobado. Ejecutando pasos…", thread_ts=thread_ts)

        async def on_step(msg: str, _report: dict) -> None:
            if msg:
                await say(f"↳ {msg}", thread_ts=thread_ts)

        result = await schedule_execute_async(plan_id, user_id, on_step_message=on_step)
        if result.get("error"):
            await say(f"Error al ejecutar: {result['error']}", thread_ts=thread_ts)
            _clear_pending(key, plan_id)
            return True

        payload = await wait_for_plan_completion(plan_id, user_id, timeout=90.0)
        if payload:
            if payload.get("trace"):
                trace_store.add(payload["session_id"], payload["trace"])
            await say(payload.get("text") or "Ejecución completada.", thread_ts=thread_ts)
        else:
            await say(
                "La ejecución sigue en curso o falló. Consulte el escritorio web para el resultado.",
                thread_ts=thread_ts,
            )
        _clear_pending(key, plan_id)
        return True

    if _find_pending_plan_id(key, user_id):
        await say(
            "Hay un plan pendiente. Responda *EJECUTAR* o *CAMBIOS: motivo*.",
            thread_ts=thread_ts,
        )
        return True

    session_id = _session_id(user_id)
    plan, err = create_execution_plan(
        message=stripped,
        channel="slack",
        session_id=session_id,
        user_id=user_id,
    )
    if err or not plan:
        return False

    _pending_plans[key] = plan.plan_id
    _attach_slack_thread_key(plan.plan_id, key)
    await say(_format_plan_message(plan.to_dict()), thread_ts=thread_ts)
    return True

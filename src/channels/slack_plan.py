"""Flujo de plan de ejecución para Slack (Fase 2 — sprint B)."""

from __future__ import annotations

import logging
import re

from src.agents.planner import approve_plan, create_execution_plan
from src.agents.plan_executor import get_plan_result, schedule_execute_async, wait_for_plan_completion
from src.agents.skill_catalog import agent_display_name
from src.gateway.trace import trace_store

logger = logging.getLogger(__name__)

_EXECUTE_RE = re.compile(r"^\s*(ejecutar|aprobar|si|s[ií]|ok|run)\s*$", re.I)

# thread_ts (o user dm) -> plan_id pendiente de aprobación
_pending_plans: dict[str, str] = {}


def _thread_key(thread_ts: str | None, user_id: str) -> str:
    return thread_ts or f"dm:{user_id}"


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
        _pending_plans.pop(key, None)
        await say(
            "Entendido. Envíe una nueva consulta y generaré otro plan.",
            thread_ts=thread_ts,
        )
        return True

    if _EXECUTE_RE.match(stripped):
        plan_id = _pending_plans.get(key)
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
        _pending_plans.pop(key, None)
        return True

    if key in _pending_plans:
        await say(
            "Hay un plan pendiente. Responda *EJECUTAR* o *CAMBIOS: motivo*.",
            thread_ts=thread_ts,
        )
        return True

    session_id = f"slack:{user_id}"
    plan, err = create_execution_plan(
        message=stripped,
        channel="slack",
        session_id=session_id,
        user_id=user_id,
    )
    if err or not plan:
        return False

    _pending_plans[key] = plan.plan_id
    await say(_format_plan_message(plan.to_dict()), thread_ts=thread_ts)
    return True

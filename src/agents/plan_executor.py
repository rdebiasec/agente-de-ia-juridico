"""Ejecución de planes aprobados con streaming SSE (Fase 2)."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from typing import Any

from agents import Runner
from agents.run_config import RunConfig

from src.agents.execution_schemas import AgentIOReport, ArtifactRef, ExecutionPlan, PlanStep
from src.agents.guardrails import apply_output_guardrails, needs_human_review
from src.agents.orchestrator import get_agent_by_id
from src.agents.pipeline import attach_session_continuity, run_post_validations, run_pre_validations
from src.agents.plan_events import PlanEventBroker
from src.agents.planner import approve_plan
from src.agents.runner import (
    _TraceRunHooks,
    _append_action,
    _base_trace,
    _fallback_response,
    _finalize_trace,
    _kan_for_agent,
    _maybe_create_draft,
    _summarize_input,
    _trace_step,
)
from src.agents.skill_catalog import agent_display_name
from src.config import get_settings
from src.gateway.agent_session import RepositoryAgentSession, reconcile_turn_messages
from src.gateway.expediente import expediente_store
from src.storage import get_repository

logger = logging.getLogger(__name__)

_PREVIEW_MAX = 200
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_RADICADO_RE = re.compile(r"\b\d{10,23}\b")


def _mask_sensitive(text: str) -> str:
    masked = _EMAIL_RE.sub("[email]", text)
    return _RADICADO_RE.sub("[radicado]", masked)


def _redact_preview(value: Any) -> Any:
    """Trunca y enmascara previews SSE step_io (SEC-07)."""
    if isinstance(value, str):
        masked = _mask_sensitive(value)
        if len(masked) > _PREVIEW_MAX:
            return masked[:_PREVIEW_MAX] + "…"
        return masked
    if isinstance(value, dict):
        return {key: _redact_preview(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_preview(item) for item in value]
    return value

TRACE_VERSION = "5.0"
_running_tasks: dict[str, asyncio.Task[None]] = {}


def _enrich_trace_v5(trace: dict, plan: ExecutionPlan) -> None:
    trace["trace_version"] = TRACE_VERSION
    trace["execution_plan_id"] = plan.plan_id
    trace["plan_status"] = plan.status
    trace.setdefault("plan_steps", [s.model_dump() for s in plan.steps])
    trace.setdefault("agent_io_reports", [])
    trace.setdefault("user_updates", [])


def _save_plan(record, plan: ExecutionPlan, *, extra: dict | None = None) -> None:
    payload = plan.to_dict()
    if extra:
        payload.update(extra)
    record.status = plan.status
    record.payload = payload
    get_repository().save_execution_plan(record)


def _persist_stream_event(record, event: dict[str, Any]) -> None:
    """Append incremental SSE event to execution_plans.payload for replay."""
    payload = dict(record.payload or {})
    events = list(payload.get("stream_events") or [])
    events.append(event)
    payload["stream_events"] = events
    if event.get("step_id"):
        payload["current_step_id"] = event["step_id"]
    record.payload = payload
    get_repository().save_execution_plan(record)


async def _publish_stream(
    broker: PlanEventBroker,
    record,
    plan_id: str,
    event: str,
    payload: dict[str, Any] | None = None,
    *,
    step_id: str | None = None,
) -> dict[str, Any]:
    ev = await broker.publish(plan_id, event, payload, step_id=step_id)
    _persist_stream_event(record, ev)
    return ev


def _step_fallback(step: PlanStep, message: str) -> str:
    base = _fallback_response(message)
    return (
        f"[{agent_display_name(step.agent_id)} · paso {step.step_id}]\n"
        f"{step.user_summary}\n\n{base}"
    )


async def _heartbeat_loop(plan_id: str, step_id: str, stop: asyncio.Event) -> None:
    broker = PlanEventBroker.get()
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=15.0)
        except asyncio.TimeoutError:
            if not stop.is_set():
                await broker.publish(
                    plan_id,
                    "heartbeat",
                    {"step_id": step_id, "message": "Ejecutando paso…"},
                    step_id=step_id,
                )


async def _run_single_step(
    step: PlanStep,
    *,
    user_message: str,
    session_id: str,
    channel: str,
    user_id: str,
    prior_summary: str,
    trace: dict,
    plan_id: str | None = None,
    stream: bool = False,
    record=None,
) -> tuple[str, AgentIOReport]:
    settings = get_settings()
    has_key = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))
    expediente = expediente_store.get_or_create(session_id)
    exp_resumen = expediente.resumen()
    broker = PlanEventBroker.get() if stream and plan_id else None

    inputs: list[ArtifactRef] = [
        ArtifactRef(
            kind="user_message",
            ref_id="user-query",
            preview=_summarize_input(user_message),
            classification="hecho",
        )
    ]
    if exp_resumen and "sin datos" not in exp_resumen.lower():
        inputs.append(
            ArtifactRef(
                kind="expediente",
                ref_id=session_id,
                preview=_summarize_input(exp_resumen),
                classification="hecho",
            )
        )
    if prior_summary:
        inputs.append(
            ArtifactRef(
                kind="prior_step_output",
                ref_id=f"deps-{','.join(step.depends_on)}",
                preview=_summarize_input(prior_summary),
                classification="inferencia",
            )
        )

    received_from = (
        "user"
        if step.order == 1
        else (step.depends_on[-1] if step.depends_on else "coordinador_expediente_penal")
    )

    if broker and plan_id and record is not None:
        await _publish_stream(
            broker,
            record,
            plan_id,
            "step_started",
            {
                "order": step.order,
                "title": step.title,
                "agent_id": step.agent_id,
                "user_summary": step.user_summary,
                "inputs_expected": step.inputs_expected,
            },
            step_id=step.step_id,
        )
    elif broker and plan_id:
        await broker.publish(
            plan_id,
            "step_started",
            {
                "order": step.order,
                "title": step.title,
                "agent_id": step.agent_id,
                "user_summary": step.user_summary,
                "inputs_expected": step.inputs_expected,
            },
            step_id=step.step_id,
        )

    stop_hb = asyncio.Event()
    hb_task: asyncio.Task | None = None
    if broker and plan_id and has_key:
        hb_task = asyncio.create_task(_heartbeat_loop(plan_id, step.step_id, stop_hb))

    try:
        if not has_key:
            text = _step_fallback(step, user_message)
            text = apply_output_guardrails(text, channel)
            report = AgentIOReport(
                step_id=step.step_id,
                agent_id=step.agent_id,
                received_from=received_from,
                inputs=inputs,
                outputs=[
                    ArtifactRef(
                        kind="skill_output",
                        ref_id=step.skill_id or step.agent_id,
                        preview=_summarize_input(text),
                        classification="inferencia",
                    )
                ],
                user_update=f"Completé: {step.title}.",
                status="done",
            )
            return text, report

        agent = get_agent_by_id(step.agent_id)
        if agent is None:
            text = apply_output_guardrails(
                f"No pude instanciar el agente {step.agent_id}. Revise la configuración del sistema.",
                channel,
            )
            report = AgentIOReport(
                step_id=step.step_id,
                agent_id=step.agent_id,
                received_from=received_from,
                inputs=inputs,
                outputs=[],
                user_update=f"Bloqueado: agente {step.agent_id} no disponible.",
                status="blocked",
            )
            return text, report

        context = ""
        if exp_resumen and "sin datos" not in exp_resumen.lower():
            context += f"[Expediente]\n{exp_resumen}\n\n"
        if prior_summary:
            context += f"[Salida de pasos previos]\n{prior_summary}\n\n"
        prompt = (
            f"{context}"
            f"[Plan aprobado — paso {step.step_id}: {step.title}]\n"
            f"Skill: {step.skill_id or 'N/A'}\n"
            f"Instrucción operativa: {step.user_summary}\n\n"
            f"[Consulta del despacho]\n{user_message}"
        )

        trace_hooks = _TraceRunHooks(trace)
        agent_session = RepositoryAgentSession(session_id, channel=channel, user_id=user_id)
        run_config = RunConfig(
            workflow_name="firma-plan-step",
            group_id=session_id,
            trace_metadata={"plan_id": trace.get("execution_plan_id", ""), "step_id": step.step_id},
        )
        if settings.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

        try:
            result = await Runner.run(
                agent,
                prompt,
                session=agent_session,
                max_turns=min(settings.agent_max_turns, 6),
                hooks=trace_hooks,
                run_config=run_config,
            )
            text = apply_output_guardrails(result.final_output or "", channel)
            status: str = "done"
        except Exception:
            logger.exception("Fallo ejecutando paso %s", step.step_id)
            text = apply_output_guardrails(
                f"No pude completar el paso «{step.title}». Intente de nuevo o ajuste el plan.",
                channel,
            )
            status = "blocked"

        report = AgentIOReport(
            step_id=step.step_id,
            agent_id=step.agent_id,
            received_from=received_from,
            inputs=inputs,
            outputs=[
                ArtifactRef(
                    kind="skill_output",
                    ref_id=step.skill_id or step.agent_id,
                    preview=_summarize_input(text),
                    classification="inferencia",
                )
            ],
            user_update=f"Completé: {step.title}." if status == "done" else f"No completé: {step.title}.",
            status=status,  # type: ignore[arg-type]
        )
        return text, report
    finally:
        stop_hb.set()
        if hb_task:
            hb_task.cancel()
            try:
                await hb_task
            except asyncio.CancelledError:
                pass


async def execute_approved_plan(
    plan_id: str,
    user_id: str,
    *,
    stream: bool = False,
    on_step_message: Any | None = None,
) -> dict:
    """Ejecuta un plan ya aprobado; devuelve respuesta de chat + trace v5."""
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return {"error": "Plan no encontrado.", "status_code": 404}

    plan = ExecutionPlan.model_validate(
        {k: v for k, v in record.payload.items() if k in ExecutionPlan.model_fields}
    )
    if plan.initiator_user_id != user_id:
        return {"error": "Solo el iniciador puede ejecutar este plan.", "status_code": 403}
    if plan.status not in ("approved", "executing"):
        return {
            "error": f"El plan debe estar aprobado antes de ejecutar (estado: {plan.status}).",
            "status_code": 409,
        }

    broker = PlanEventBroker.get() if stream else None
    plan.status = "executing"
    _save_plan(record, plan)

    session_id = plan.session_id
    channel = plan.channel
    message = plan.user_message
    settings = get_settings()
    uid = user_id

    trace = _base_trace(session_id=session_id, channel=channel, message=message)
    _enrich_trace_v5(trace, plan)
    trace["route"] = "plan_executor"
    trace["steps"].append(_trace_step("Plan aprobado", "done", f"Ejecutando plan {plan_id}."))

    if broker:
        await _publish_stream(
            broker,
            record,
            plan_id,
            "execution_started",
            {"objective": plan.objective, "steps_count": len(plan.steps)},
        )

    chat = get_repository().get_chat_session(session_id)
    history = list(chat.messages) if chat else []
    from src.services.expediente_sync import sync_expediente_from_chat

    sync_expediente_from_chat(session_id, message, history, trace=trace)
    exp_resumen = expediente_store.get_or_create(session_id).resumen()
    ok_pre, pre_err = run_pre_validations(
        message, history=history, expediente_resumen=exp_resumen, trace=trace
    )
    prior_traces = get_repository().list_session_traces(session_id, limit=40)
    attach_session_continuity(trace, history=history, session_id=session_id, prior_traces=prior_traces)
    if not ok_pre:
        plan.status = "failed"
        _save_plan(record, plan, extra={"stream_events": broker.get_history(plan_id) if broker else []})
        trace["blocked"] = True
        text = pre_err or "Validación previa falló."
        _finalize_trace(trace, text)
        if broker:
            await _publish_stream(
                broker, record, plan_id, "plan_failed", {"error": text, "trace": trace}
            )
        return {
            "text": text,
            "agent": "guardrail",
            "pending_review": False,
            "trace": trace,
            "session_id": session_id,
            "plan_id": plan_id,
        }

    prior_summary = ""
    last_text = ""
    destination_agent = plan.agents_involved[-1] if plan.agents_involved else "coordinador_expediente_penal"
    io_reports: list[dict] = []

    for step in plan.steps:
        step.status = "in_progress"
        trace["plan_steps"] = [s.model_dump() for s in plan.steps]
        last_text, report = await _run_single_step(
            step,
            user_message=message,
            session_id=session_id,
            channel=channel,
            user_id=uid,
            prior_summary=prior_summary,
            trace=trace,
            plan_id=plan_id,
            stream=stream,
            record=record,
        )
        step.status = report.status
        io_reports.append(report.to_dict())
        trace["agent_io_reports"] = io_reports
        trace.setdefault("user_updates", []).append(
            {"at_ms": int(time.time() * 1000), "step_id": step.step_id, "message": report.user_update}
        )
        if broker:
            step_io_payload = _redact_preview(
                {
                    "report": report.to_dict(),
                    "inputs": [i.model_dump() for i in report.inputs],
                    "outputs": [o.model_dump() for o in report.outputs],
                }
            )
            await _publish_stream(
                broker,
                record,
                plan_id,
                "step_io",
                step_io_payload,
                step_id=step.step_id,
            )
            await _publish_stream(
                broker,
                record,
                plan_id,
                "step_done",
                {"status": report.status, "user_update": report.user_update},
                step_id=step.step_id,
            )
        if on_step_message:
            try:
                maybe = on_step_message(report.user_update, report.to_dict())
                if asyncio.iscoroutine(maybe):
                    await maybe
            except Exception:
                logger.exception("on_step_message falló para plan %s", plan_id)

        prior_summary = f"{prior_summary}\n\n--- {step.title} ---\n{last_text}".strip()
        destination_agent = step.agent_id
        trace["steps"].append(
            _trace_step(
                f"Paso {step.order}: {step.title}",
                report.status,
                report.user_update,
            )
        )

    text = run_post_validations(message, last_text, trace)
    pending_review = needs_human_review(text, channel, message) or any(
        s.requires_hitl_output for s in plan.steps
    )
    trace["sent_to_agent"] = destination_agent
    trace["selected_agent"] = destination_agent
    trace["skill_kan"] = _kan_for_agent(destination_agent)
    trace["skill_reason"] = f"Ejecución del plan aprobado {plan_id}."
    trace["human_review_required"] = pending_review
    trace["blocked"] = False

    draft_id = None
    if pending_review:
        draft_id = _maybe_create_draft(
            session_id=session_id,
            message=message,
            text=text,
            destination_agent=destination_agent,
            trace=trace,
        )
    _append_action(
        trace,
        action_type="plan_execution",
        status="done",
        actor="plan_executor",
        detail=f"Plan {plan_id} ejecutado con {len(plan.steps)} paso(s).",
    )
    trace["steps"].append(
        _trace_step(
            "Revisión humana",
            "pending" if pending_review else "done",
            "Pendiente de aprobación del abogado." if pending_review else "No requiere aprobación adicional.",
        )
    )

    plan.status = "done"
    result_payload = {
        "text": text,
        "agent": destination_agent,
        "pending_review": pending_review,
        "draft_id": draft_id,
        "session_id": session_id,
        "trace": trace,
        "plan_id": plan_id,
    }
    _save_plan(
        record,
        plan,
        extra={
            "agent_io_reports": io_reports,
            "result": result_payload,
            "stream_events": broker.get_history(plan_id) if broker else record.payload.get("stream_events", []),
        },
    )

    _finalize_trace(trace, text)
    get_repository().append_chat_message(
        session_id, channel=channel, user_id=uid, role="user", content=message,
        max_messages=settings.session_max_messages,
    )
    get_repository().append_chat_message(
        session_id, channel=channel, user_id=uid, role="assistant", content=text,
        max_messages=settings.session_max_messages,
    )
    reconcile_turn_messages(session_id, user_text=message, assistant_text=text)

    if broker:
        from src.gateway.trace import trace_store

        trace_store.add(session_id, trace)
        await _publish_stream(broker, record, plan_id, "plan_done", result_payload)

    return result_payload


async def _run_scheduled(plan_id: str, user_id: str, on_step_message: Any | None = None) -> None:
    broker = PlanEventBroker.get()
    try:
        result = await execute_approved_plan(
            plan_id, user_id, stream=True, on_step_message=on_step_message
        )
        if "error" in result:
            record = get_repository().get_execution_plan(plan_id)
            if record:
                await _publish_stream(
                    broker, record, plan_id, "plan_failed", {"error": result["error"]}
                )
            else:
                await broker.publish(plan_id, "plan_failed", {"error": result["error"]})
    except Exception as exc:
        logger.exception("Ejecución programada falló para plan %s", plan_id)
        record = get_repository().get_execution_plan(plan_id)
        if record:
            plan = ExecutionPlan.model_validate(
                {k: v for k, v in record.payload.items() if k in ExecutionPlan.model_fields}
            )
            plan.status = "failed"
            _save_plan(record, plan, extra={"stream_events": broker.get_history(plan_id)})
            await _publish_stream(broker, record, plan_id, "plan_failed", {"error": str(exc)})
        else:
            await broker.publish(plan_id, "plan_failed", {"error": str(exc)})
    finally:
        await broker.close(plan_id)
        _running_tasks.pop(plan_id, None)


async def schedule_execute_async(
    plan_id: str,
    user_id: str,
    *,
    on_step_message: Any | None = None,
) -> dict:
    """Lanza ejecución en background (Fase 2). Idempotente si ya está en curso."""
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return {"error": "Plan no encontrado.", "status_code": 404}

    plan = ExecutionPlan.model_validate(
        {k: v for k, v in record.payload.items() if k in ExecutionPlan.model_fields}
    )
    if plan.initiator_user_id != user_id:
        return {"error": "Solo el iniciador puede ejecutar este plan.", "status_code": 403}
    if plan.status == "executing" and plan_id in _running_tasks:
        return {"ok": True, "plan_id": plan_id, "status": "executing"}
    if plan.status == "failed":
        plan.status = "approved"
        for step in plan.steps:
            step.status = "pending"
        _save_plan(record, plan)
    elif plan.status != "approved":
        return {
            "error": f"El plan debe estar aprobado (estado: {plan.status}).",
            "status_code": 409,
        }

    broker = PlanEventBroker.get()
    await broker.reset_plan(plan_id)
    task = asyncio.create_task(_run_scheduled(plan_id, user_id, on_step_message))
    _running_tasks[plan_id] = task
    return {"ok": True, "plan_id": plan_id, "status": "executing"}


async def wait_for_plan_completion(
    plan_id: str,
    user_id: str,
    *,
    timeout: float = 90.0,
) -> dict | None:
    """Espera la tarea en curso y devuelve el resultado persistido."""
    task = _running_tasks.get(plan_id)
    if task is not None:
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    final = get_plan_result(plan_id, user_id)
    if final.get("result"):
        return final["result"]
    return None


def get_plan_result(plan_id: str, user_id: str) -> dict:
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return {"error": "Plan no encontrado.", "status_code": 404}
    if record.initiator_user_id != user_id:
        return {"error": "No autorizado.", "status_code": 403}
    result = (record.payload or {}).get("result")
    if not result:
        return {"error": "Resultado aún no disponible.", "status_code": 404, "status": record.status}
    return {"ok": True, "status": record.status, "result": result}


async def approve_and_execute(plan_id: str, user_id: str) -> dict:
    """Compatibilidad Fase 1 — ejecución síncrona sin SSE."""
    plan, err = approve_plan(plan_id, user_id)
    if err:
        return {"error": err, "status_code": 400}
    result = await execute_approved_plan(plan_id, user_id, stream=False)
    if "error" in result:
        return result
    result["plan"] = plan.to_dict() if plan else None
    return result

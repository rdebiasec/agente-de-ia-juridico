"""Ejecución de planes aprobados con streaming SSE (Fase 2)."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
import uuid
from typing import Any

from agents import Runner
from agents.run_config import RunConfig

from src.agents.execution_schemas import AgentIOReport, ArtifactRef, ExecutionPlan, PlanStep
from src.agents.context_security import wrap_untrusted_context
from src.agents.guardrails import apply_output_guardrails, needs_human_review
from src.agents.orchestrator import (
    POC_AGENT_ID,
    SPECIALIST_AGENT_IDS,
    build_coordinador_agent,
    get_agent_by_id,
)
from src.agents.pipeline import attach_session_continuity, run_post_validations, run_pre_validations
from src.agents.plan_events import PlanEventBroker
from src.agents.planner import approve_plan
from src.agents.resilience import run_with_retries
from src.agents.runner import (
    _TraceRunHooks,
    AgentBudgetExceeded,
    _append_action,
    _base_trace,
    _ensure_poc_voice,
    _fallback_response,
    _finalize_trace,
    _kan_for_agent,
    _maybe_create_draft,
    _summarize_input,
    _trace_step,
)
from src.agents.session_context import FirmRunContext, bind_run_context
from src.agents.skill_catalog import agent_display_name, skill_contract_brief
from src.config import get_settings
from src.gateway.agent_session import reconcile_turn_messages
from src.gateway.expediente import expediente_store
from src.storage import get_repository

logger = logging.getLogger(__name__)

_PREVIEW_MAX = 200
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_RADICADO_RE = re.compile(r"\b\d{10,23}\b")


def _plan_step_session_id(lawyer_session_id: str, plan_id: str | None, step_id: str) -> str:
    """Sesión aislada: no contamina el historial del chat del abogado."""
    plan_part = plan_id or "orphan"
    return f"{lawyer_session_id}:plan:{plan_part}:{step_id}"


def _step_prompt(
    step: PlanStep,
    *,
    user_message: str,
    exp_resumen: str,
    prior_summary: str,
) -> str:
    """Prompt del paso: al especialista real o al POC, segun agent_id del plan."""
    context = ""
    if exp_resumen and "sin datos" not in exp_resumen.lower():
        wrapped, _ = wrap_untrusted_context(exp_resumen, label="EXPEDIENTE")
        context += f"[Expediente]\n{wrapped}\n\n"
    if prior_summary:
        wrapped, _ = wrap_untrusted_context(
            prior_summary,
            label="SALIDAS DE PASOS PREVIOS",
        )
        context += f"[Salida de pasos previos]\n{wrapped}\n\n"

    if step.agent_id == POC_AGENT_ID:
        directive = (
            "Ejecuta este paso como Gerente del Caso Penal (coordinador). "
            "Clasifica, verifica completitud y cierra el paso sin ceder la voz."
        )
    elif step.agent_id in SPECIALIST_AGENT_IDS:
        directive = (
            "Ejecuta este paso como especialista de BACKOFFICE (equipo interno). "
            "Devuelve hallazgos operativos claros para que el Gerente del Caso sintetice. "
            "No saludes al abogado ni firmes como interlocutor del despacho. "
            "Ajusta la salida al contrato de capacidad del paso."
        )
    else:
        directive = "Responde con la informacion disponible del expediente y la consulta."

    contract = skill_contract_brief(step.skill_id)
    contract_block = f"{contract}\n\n" if contract else ""

    return (
        f"{context}"
        f"[Plan aprobado — paso {step.step_id}: {step.title}]\n"
        f"Skill/contrato: {step.skill_id or 'N/A'}\n"
        f"Instruccion operativa: {step.user_summary}\n"
        f"{directive}\n\n"
        f"{contract_block}"
        f"[Consulta del despacho]\n{user_message}"
    )


# Compatibilidad con imports/tests previos.
_poc_step_prompt = _step_prompt


def _resolve_step_agent(step: PlanStep):
    """Instancia el agente declarado en el paso (fidelity plan↔ejecucion)."""
    if step.agent_id in SPECIALIST_AGENT_IDS:
        agent = get_agent_by_id(step.agent_id)
        if agent is not None:
            return agent
    return build_coordinador_agent()


def _final_output_text(result: Any) -> str:
    from src.agents.structured_render import render_structured_output

    output = getattr(result, "final_output", None)
    return render_structured_output(output)


def _quality_gate_blocks(result: Any, step: PlanStep) -> tuple[bool, str]:
    """Gate duro: DictamenCalidad rechazado/escalar bloquea entrega accionable."""
    if step.agent_id != "analista_calidad_juridica":
        return False, ""
    from src.agents.structured_render import extract_dictamen_calidad

    raw = getattr(result, "final_output", None)
    dictamen = extract_dictamen_calidad(raw)
    if not dictamen:
        # Sin estructura: no bloquear por falso negativo; el guardrail de calidad ya tripwirea.
        return False, ""
    veredicto = str(dictamen.get("veredicto") or "").strip().lower()
    if veredicto not in ("rechazado", "escalar"):
        return False, ""
    resumen = str(dictamen.get("resumen") or "").strip()
    hallazgos = dictamen.get("hallazgos") or []
    detalle = resumen or "; ".join(str(h) for h in hallazgos[:5]) or "sin detalle"
    msg = (
        f"⛔ Control de calidad jurídica: veredicto **{veredicto}**. "
        "No se entrega salida final accionable hasta revisión del abogado. "
        f"Detalle: {detalle}"
    )
    return True, msg


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
    payload = dict(record.payload or {})
    payload.update(plan.to_dict())
    if extra:
        payload.update(extra)
    record.status = plan.status
    record.payload = payload
    get_repository().save_execution_plan(record)


def _ordered_plan_steps(steps: list[PlanStep]) -> list[PlanStep]:
    """Orden topológico estable; rechaza referencias ausentes, duplicados y ciclos."""
    by_id = {step.step_id: step for step in steps}
    if len(by_id) != len(steps):
        raise ValueError("El plan contiene step_id duplicado.")
    missing = sorted(
        {
            dependency
            for step in steps
            for dependency in step.depends_on
            if dependency not in by_id
        }
    )
    if missing:
        raise ValueError(f"Dependencias inexistentes: {', '.join(missing)}.")

    pending = set(by_id)
    completed: set[str] = set()
    ordered: list[PlanStep] = []
    while pending:
        ready = [
            by_id[step_id]
            for step_id in pending
            if set(by_id[step_id].depends_on).issubset(completed)
        ]
        if not ready:
            raise ValueError("El plan contiene un ciclo de dependencias.")
        ready.sort(key=lambda step: (step.order, step.step_id))
        for step in ready:
            ordered.append(step)
            completed.add(step.step_id)
            pending.remove(step.step_id)
    return ordered


def _checkpoint_payload(
    *,
    owner: str,
    step: PlanStep | None,
    outputs_by_step: dict[str, str],
) -> dict[str, Any]:
    return {
        "execution_owner": owner,
        "checkpoint_at_ms": int(time.time() * 1000),
        "current_step_id": step.step_id if step else None,
        "step_outputs": outputs_by_step,
    }


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
            text = apply_output_guardrails(
                text,
                channel,
                allow_sensitive_pii=True,
            )
            from src.agents.completeness import record_specialist_result

            ledger_result = record_specialist_result(
                session_id,
                agent_id=step.agent_id,
                text=text,
                status="done",
            )
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
                structured_output=ledger_result,
                user_update=f"↳ Completé: {step.title}.",
                status="done",
            )
            return text, report

        agent = _resolve_step_agent(step)
        prompt = _step_prompt(
            step,
            user_message=user_message,
            exp_resumen=exp_resumen,
            prior_summary=prior_summary,
        )

        trace_hooks = _TraceRunHooks(trace)
        # Sin session del abogado: el plan no escribe turns de especialistas en el chat.
        run_config = RunConfig(
            workflow_name="firma-plan-step",
            group_id=_plan_step_session_id(session_id, plan_id, step.step_id),
            trace_metadata={
                "plan_id": trace.get("execution_plan_id", ""),
                "step_id": step.step_id,
                "step_agent_id": step.agent_id,
                "runtime_agent": getattr(agent, "name", step.agent_id),
            },
        )
        if settings.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

        try:
            from agents.exceptions import (
                InputGuardrailTripwireTriggered,
                OutputGuardrailTripwireTriggered,
            )

            async def _on_retry(attempt: int, exc: BaseException, delay: float) -> None:
                fallback_model = (settings.openai_model_fallback or "").strip()
                if fallback_model:
                    agent.model = fallback_model
                trace.setdefault("spans", []).append(
                    {
                        "name": f"plan:{step.step_id}:reintento",
                        "kind": "resilience",
                        "status": "pending",
                        "detail": (
                            f"Fallo transitorio {type(exc).__name__}; "
                            f"reintento en {delay:.2f}s."
                        ),
                        "at_ms": int(time.time() * 1000),
                    }
                )

            firm_ctx = FirmRunContext(
                session_id=session_id,
                expediente_id=session_id,
                channel=channel,
                user_id=user_id,
                involucra_menor=bool(getattr(expediente, "involucra_menor", False)),
                datos_sensibles=bool(getattr(expediente, "datos_sensibles", False)),
            )
            with bind_run_context(firm_ctx):
                result = await run_with_retries(
                    lambda: Runner.run(
                        agent,
                        prompt,
                        session=None,
                        context=firm_ctx,
                        # Watchdog por criticidad: especialistas acotados.
                        max_turns=(
                            min(settings.agent_max_turns_plan_step, 4)
                            if step.agent_id in SPECIALIST_AGENT_IDS
                            else min(
                                settings.agent_max_turns,
                                settings.agent_max_turns_plan_step,
                            )
                        ),
                        hooks=trace_hooks,
                        run_config=run_config,
                    ),
                    max_retries=settings.agent_max_retries,
                    timeout_seconds=settings.agent_plan_step_timeout_seconds,
                    on_retry=_on_retry,
                    non_retryable=(
                        InputGuardrailTripwireTriggered,
                        OutputGuardrailTripwireTriggered,
                        AgentBudgetExceeded,
                    ),
                )
            if result is None:  # pragma: no cover
                raise RuntimeError("El paso terminó sin resultado.")
            blocked_quality, quality_msg = _quality_gate_blocks(result, step)
            text = apply_output_guardrails(
                quality_msg if blocked_quality else _final_output_text(result),
                channel,
                allow_sensitive_pii=True,
            )
            last_agent_name = getattr(getattr(result, "last_agent", None), "name", None) or getattr(
                agent, "name", POC_AGENT_ID
            )
            text = _ensure_poc_voice(
                text,
                last_agent_name=last_agent_name,
                backoffice_agent=step.agent_id if step.agent_id in SPECIALIST_AGENT_IDS else POC_AGENT_ID,
            )
            status: str = "blocked" if blocked_quality else "done"
            if blocked_quality:
                trace.setdefault("spans", []).append(
                    {
                        "name": f"plan:{step.step_id}:quality_gate",
                        "kind": "quality_gate",
                        "status": "blocked",
                        "detail": quality_msg,
                        "at_ms": int(time.time() * 1000),
                    }
                )
                trace["quality_gate"] = {
                    "blocked": True,
                    "step_id": step.step_id,
                    "message": quality_msg,
                }
        except AgentBudgetExceeded as exc:
            logger.warning("Presupuesto excedido en paso %s: %s", step.step_id, exc)
            text = apply_output_guardrails(
                f"Detuve el paso «{step.title}» porque alcanzó el presupuesto operativo. "
                "Reduzca el alcance del paso o continúe con un plan más corto.",
                channel,
            )
            status = "blocked"
            trace.setdefault("spans", []).append(
                {
                    "name": f"plan:{step.step_id}:budget",
                    "kind": "resilience",
                    "status": "blocked",
                    "detail": str(exc),
                    "at_ms": int(time.time() * 1000),
                }
            )
        except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as exc:
            logger.warning("Guardrail tripwire en paso %s: %s", step.step_id, exc)
            text = apply_output_guardrails(
                "No puedo continuar con este paso: la consulta o la salida no cumplen "
                "los límites del despacho penal-víctimas. Reformule o aporte el ancla penal.",
                channel,
            )
            status = "blocked"
        except Exception:
            logger.exception("Fallo ejecutando paso %s", step.step_id)
            text = apply_output_guardrails(
                f"No pude completar el paso «{step.title}». Intente de nuevo o ajuste el plan.",
                channel,
            )
            status = "blocked"

        from src.agents.completeness import record_specialist_result

        ledger_result = record_specialist_result(
            session_id,
            agent_id=step.agent_id,
            text=text,
            status=status,
        )
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
            structured_output=ledger_result,
            user_update=(
                f"↳ Completé: {step.title}."
                if status == "done"
                else f"↳ No completé: {step.title}."
            ),
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

    settings = get_settings()
    if plan.status == "executing":
        checkpoint_at = int((record.payload or {}).get("checkpoint_at_ms") or 0)
        age_seconds = max(0.0, (time.time() * 1000 - checkpoint_at) / 1000)
        if checkpoint_at and age_seconds < settings.plan_stale_after_seconds:
            return {
                "error": "El plan ya está siendo ejecutado por otro worker.",
                "status_code": 409,
                "status": "executing",
            }

    try:
        ordered_steps = _ordered_plan_steps(plan.steps)
    except ValueError as exc:
        plan.status = "failed"
        _save_plan(record, plan, extra={"failure_reason": str(exc)})
        return {"error": str(exc), "status_code": 409, "status": "failed"}

    broker = PlanEventBroker.get() if stream else None
    execution_owner = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    plan.status = "executing"
    outputs_by_step = dict((record.payload or {}).get("step_outputs") or {})
    _save_plan(
        record,
        plan,
        extra=_checkpoint_payload(
            owner=execution_owner,
            step=None,
            outputs_by_step=outputs_by_step,
        ),
    )

    session_id = plan.session_id
    channel = plan.channel
    message = plan.user_message
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
    expediente = expediente_store.get_or_create(session_id)
    exp_resumen = expediente.resumen()
    requested_destination = (plan.triage_snapshot or {}).get(
        "agente_destino", "coordinador_expediente_penal"
    )
    ok_pre, pre_err = run_pre_validations(
        message,
        history=history,
        expediente_resumen=exp_resumen,
        trace=trace,
        expediente=expediente,
        destination=requested_destination,
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
    io_reports: list[dict] = list((record.payload or {}).get("agent_io_reports") or [])
    execution_failed = False

    for step in ordered_steps:
        if step.status == "done" and step.step_id in outputs_by_step:
            continue
        dependency_statuses = {
            dependency: next(
                (candidate.status for candidate in plan.steps if candidate.step_id == dependency),
                "missing",
            )
            for dependency in step.depends_on
        }
        if any(status != "done" for status in dependency_statuses.values()):
            step.status = "skipped"
            execution_failed = True
            last_text = (
                f"No se ejecutó «{step.title}»: una dependencia no terminó correctamente."
            )
            break

        step.status = "in_progress"
        trace["plan_steps"] = [s.model_dump() for s in plan.steps]
        dependency_outputs = [
            outputs_by_step[dependency]
            for dependency in step.depends_on
            if dependency in outputs_by_step
        ]
        prior_summary = "\n\n".join(dependency_outputs)
        _save_plan(
            record,
            plan,
            extra=_checkpoint_payload(
                owner=execution_owner,
                step=step,
                outputs_by_step=outputs_by_step,
            ),
        )
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
        outputs_by_step[step.step_id] = last_text
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

        destination_agent = step.agent_id
        trace["steps"].append(
            _trace_step(
                f"Paso {step.order}: {step.title}",
                report.status,
                report.user_update,
            )
        )
        _save_plan(
            record,
            plan,
            extra={
                **_checkpoint_payload(
                    owner=execution_owner,
                    step=step,
                    outputs_by_step=outputs_by_step,
                ),
                "agent_io_reports": io_reports,
            },
        )
        if report.status != "done":
            execution_failed = True
            for remaining in ordered_steps:
                if remaining.status == "pending":
                    remaining.status = "skipped"
            break

    if execution_failed:
        completed_count = sum(step.status == "done" for step in plan.steps)
        plan.status = "partial" if completed_count else "failed"
        text = apply_output_guardrails(
            last_text
            or "El plan se detuvo porque un paso crítico no pudo completarse.",
            channel,
        )
        trace["blocked"] = True
        trace["plan_status"] = plan.status
        trace["plan_steps"] = [step.model_dump() for step in plan.steps]
        result_payload = {
            "text": text,
            "agent": POC_AGENT_ID,
            "pending_review": False,
            "session_id": session_id,
            "trace": trace,
            "plan_id": plan_id,
            "status": plan.status,
        }
        _save_plan(
            record,
            plan,
            extra={
                **_checkpoint_payload(
                    owner=execution_owner,
                    step=None,
                    outputs_by_step=outputs_by_step,
                ),
                "agent_io_reports": io_reports,
                "result": result_payload,
            },
        )
        _finalize_trace(trace, text)
        if broker:
            await _publish_stream(
                broker,
                record,
                plan_id,
                "plan_failed",
                {"error": text, "status": plan.status, "trace": trace},
            )
        return result_payload

    text = run_post_validations(message, last_text, trace)
    text = _ensure_poc_voice(
        text,
        last_agent_name=POC_AGENT_ID,
        backoffice_agent=destination_agent if destination_agent in SPECIALIST_AGENT_IDS else POC_AGENT_ID,
    )
    pending_review = needs_human_review(text, channel, message) or any(
        s.requires_hitl_output for s in plan.steps
    )
    # Cara al abogado = POC; backoffice queda en sent_to_agent / selected_agent.
    trace["sent_to_agent"] = destination_agent
    trace["selected_agent"] = destination_agent
    trace["skill_kan"] = _kan_for_agent(destination_agent)
    trace["skill_reason"] = (
        f"Plan {plan_id} ejecutado paso-a-paso con agente declarado "
        f"(ultimo backoffice: {destination_agent}); voz al abogado: POC."
    )
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
        detail=(
            f"Plan {plan_id} ejecutado con {len(plan.steps)} paso(s); "
            "cada paso instancio su agent_id (no orquestador completo)."
        ),
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
        "agent": POC_AGENT_ID,
        "pending_review": pending_review,
        "draft_id": draft_id,
        "session_id": session_id,
        "trace": trace,
        "plan_id": plan_id,
        "status": "done",
    }
    _save_plan(
        record,
        plan,
        extra={
            **_checkpoint_payload(
                owner=execution_owner,
                step=None,
                outputs_by_step=outputs_by_step,
            ),
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
    if plan.status == "executing":
        if plan_id in _running_tasks:
            return {"ok": True, "plan_id": plan_id, "status": "executing"}
        checkpoint_at = int((record.payload or {}).get("checkpoint_at_ms") or 0)
        age_seconds = max(0.0, (time.time() * 1000 - checkpoint_at) / 1000)
        if checkpoint_at and age_seconds < get_settings().plan_stale_after_seconds:
            return {"ok": True, "plan_id": plan_id, "status": "executing"}
        plan.status = "approved"
        for step in plan.steps:
            if step.status == "in_progress":
                step.status = "pending"
        _save_plan(record, plan, extra={"recovered_from_stale_execution": True})
    elif plan.status == "failed":
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


def recover_stale_executions() -> int:
    """Marca para reanudación planes huérfanos tras restart/deploy.

    No ejecuta trabajo durante el arranque; el próximo pedido de ejecución
    reanuda desde los checkpoints `done`, evitando duplicar pasos completados.
    """
    now_ms = int(time.time() * 1000)
    stale_after_ms = get_settings().plan_stale_after_seconds * 1000
    recovered = 0
    for record in get_repository().list_execution_plans(limit=500):
        if record.status != "executing":
            continue
        checkpoint_at = int((record.payload or {}).get("checkpoint_at_ms") or 0)
        if checkpoint_at and now_ms - checkpoint_at < stale_after_ms:
            continue
        plan = ExecutionPlan.model_validate(
            {key: value for key, value in record.payload.items() if key in ExecutionPlan.model_fields}
        )
        plan.status = "approved"
        for step in plan.steps:
            if step.status == "in_progress":
                step.status = "pending"
        _save_plan(
            record,
            plan,
            extra={
                "recovered_from_stale_execution": True,
                "recovered_at_ms": now_ms,
            },
        )
        recovered += 1
    return recovered


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

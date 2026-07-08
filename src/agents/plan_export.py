"""Export Markdown de planes de ejecución (Fase 3)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.agents.execution_schemas import ExecutionPlan
from src.agents.plan_templates import template_label
from src.agents.skill_catalog import agent_display_name
from src.storage.models import ExecutionPlanRecord


def _fmt_ms(ms: int | None) -> str:
    if not ms:
        return "—"
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def render_plan_markdown(
    plan: ExecutionPlan,
    *,
    io_reports: list[dict[str, Any]] | None = None,
    trace_summary: str = "",
    result_text: str = "",
) -> str:
    kind = plan.template_kind or "generico"
    lines: list[str] = [
        "# Plan de ejecución — trazabilidad despacho",
        "",
        f"**Plan ID:** `{plan.plan_id}`",
        f"**Sesión:** `{plan.session_id}`",
        f"**Estado:** {plan.status}",
        f"**Plantilla:** {template_label(kind)} (`{kind}`)",
        f"**Creado:** {_fmt_ms(plan.created_at_ms)}",
        f"**Aprobado:** {_fmt_ms(plan.approved_at_ms)}",
        "",
        "## Consulta del despacho",
        "",
        plan.user_message.strip() or "—",
        "",
        "## Objetivo",
        "",
        plan.objective.strip() or "—",
        "",
        "## Pasos planificados",
        "",
    ]

    for step in plan.steps:
        lines.append(f"### Paso {step.order} — {step.title}")
        lines.append(f"- **Agente:** {agent_display_name(step.agent_id)} (`{step.agent_id}`)")
        lines.append(f"- **Estado:** {step.status}")
        lines.append(f"- **Resumen:** {step.user_summary}")
        if step.inputs_expected:
            lines.append(f"- **Entradas esperadas:** {', '.join(step.inputs_expected)}")
        if step.outputs_promised:
            lines.append(f"- **Salidas prometidas:** {', '.join(step.outputs_promised)}")
        lines.append("")

    if io_reports:
        lines.extend(["## Informes I/O por paso", ""])
        for report in io_reports:
            lines.append(f"### {report.get('step_id', '—')} — {agent_display_name(report.get('agent_id', ''))}")
            lines.append(f"- **Estado:** {report.get('status', '—')}")
            if report.get("user_update"):
                lines.append(f"- **Actualización:** {report['user_update']}")
            for inp in report.get("inputs") or []:
                preview = (inp.get("preview") or "")[:200]
                lines.append(f"- **Entrada ({inp.get('kind', '?')}):** {preview}")
            for out in report.get("outputs") or []:
                preview = (out.get("preview") or "")[:200]
                lines.append(f"- **Salida ({out.get('kind', '?')}):** {preview}")
            lines.append("")

    if result_text.strip():
        lines.extend(["## Resultado final", "", result_text.strip(), ""])

    if trace_summary.strip():
        lines.extend(["## Resumen de traza", "", trace_summary.strip(), ""])

    lines.extend(
        [
            "---",
            "",
            "_Export generado por Agente Jurídico — la IA propone; el abogado revisa y aprueba._",
            "",
        ]
    )
    return "\n".join(lines)


def markdown_from_record(record: ExecutionPlanRecord) -> str:
    plan = ExecutionPlan.model_validate(
        {k: v for k, v in (record.payload or {}).items() if k in ExecutionPlan.model_fields}
    )
    payload = record.payload or {}
    result = payload.get("result") or {}
    trace = result.get("trace") or {}
    completion = trace.get("completion") or {}
    trace_summary = completion.get("summary") if isinstance(completion.get("summary"), str) else ""
    return render_plan_markdown(
        plan,
        io_reports=payload.get("agent_io_reports") or [],
        trace_summary=trace_summary,
        result_text=str(result.get("text") or ""),
    )

"""Reporte analítico de sesión Fase 0 — métricas, reglas e IA."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from html import escape
from typing import Any

from src.config import get_settings
from src.validation.rubric import CONNECTION_BLOCK, VALIDATION_BLOCKS, total_weight

logger = logging.getLogger(__name__)

BLOCK_META = [
    {"id": CONNECTION_BLOCK["id"], "title": CONNECTION_BLOCK["title"], "weight": CONNECTION_BLOCK["weight"]},
    *[{"id": b["id"], "title": b["title"], "weight": b["weight"]} for b in VALIDATION_BLOCKS],
]

BLOCK_TITLES = {b["id"]: b["title"] for b in BLOCK_META}


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_metrics(session: dict[str, Any]) -> dict[str, Any]:
    marks: dict[str, str] = session.get("marks") or {}
    chat_log: list[dict] = session.get("chatLog") or []
    events: list[dict] = session.get("events") or []
    checklist: dict = session.get("checklistChecked") or {}

    total = total_weight()
    score = sum(b["weight"] for b in BLOCK_META if marks.get(b["id"]) == "pass")
    passed = sum(1 for b in BLOCK_META if marks.get(b["id"]) == "pass")
    failed = sum(1 for b in BLOCK_META if marks.get(b["id"]) == "fail")
    pending = len(BLOCK_META) - passed - failed

    user_msgs = [m for m in chat_log if m.get("role") == "user"]
    assistant_msgs = [m for m in chat_log if m.get("role") == "assistant"]
    probe_msgs = [m for m in user_msgs if m.get("via") == "probe"]
    manual_msgs = [m for m in user_msgs if m.get("via") != "probe"]

    latencies = [m["latencyMs"] for m in assistant_msgs if isinstance(m.get("latencyMs"), (int, float))]
    avg_latency_ms = round(sum(latencies) / len(latencies)) if latencies else None

    checklist_total = 7
    checklist_done = sum(1 for v in checklist.values() if v)
    generate_events = [e for e in events if e.get("type") == "generate_probes"]

    started = _parse_iso(session.get("startedAt"))
    last = _parse_iso(session.get("lastActivityAt"))
    duration_min = None
    if started and last:
        duration_min = max(0, round((last - started).total_seconds() / 60, 1))

    sections = []
    for block in BLOCK_META:
        bid = block["id"]
        mark = marks.get(bid)
        linked = [m for m in chat_log if m.get("blockId") == bid]
        sections.append(
            {
                "id": bid,
                "title": block["title"],
                "weight": block["weight"],
                "mark": mark or "pending",
                "points_earned": block["weight"] if mark == "pass" else 0,
                "interactions": len(linked),
            }
        )

    return {
        "session_id": session.get("sessionId"),
        "score": score,
        "total_weight": total,
        "score_percent": round((score / total) * 100) if total else 0,
        "sections_passed": passed,
        "sections_failed": failed,
        "sections_pending": pending,
        "checklist_done": checklist_done,
        "checklist_total": checklist_total,
        "checklist_percent": round((checklist_done / checklist_total) * 100) if checklist_total else 0,
        "chat_turns": len(user_msgs),
        "assistant_replies": len(assistant_msgs),
        "probe_questions": len(probe_msgs),
        "manual_questions": len(manual_msgs),
        "avg_latency_ms": avg_latency_ms,
        "probe_regenerations": len(generate_events),
        "duration_minutes": duration_min,
        "sections": sections,
    }


def build_rules_insights(session: dict[str, Any]) -> list[str]:
    marks: dict[str, str] = session.get("marks") or {}
    metrics = compute_metrics(session)
    insights: list[str] = []

    score = metrics["score"]
    if score == 100:
        insights.append("Puntaje máximo (100/100): todas las secciones marcadas como aprobadas.")
    elif score >= 70:
        insights.append(f"Puntaje {score}/100: desempeño aceptable con margen de mejora en secciones pendientes o rechazadas.")
    elif metrics["sections_pending"] == len(BLOCK_META):
        insights.append("Aún no hay secciones evaluadas: complete las pruebas y marque Aprobada o Rechazada.")
    else:
        insights.append(f"Puntaje {score}/100: por debajo del umbral recomendado (70). Revise secciones rechazadas con el equipo técnico.")

    critical = {
        "connection": "Conexión y Fase 0",
        "phase-block": "Bloqueo Fase 1+",
        "disclaimer": "Disclaimer legal",
        "integrity": "Integridad (no inventar datos)",
    }
    for bid, label in critical.items():
        mark = marks.get(bid)
        if mark == "fail":
            insights.append(f"CRÍTICO — {label}: marcado como rechazado. Priorizar corrección antes de avanzar de fase.")
        elif mark == "pass":
            insights.append(f"OK — {label}: aprobado por la abogada.")
        elif metrics["chat_turns"] > 0:
            insights.append(f"PENDIENTE — {label}: aún sin evaluación formal.")

    if metrics["checklist_percent"] < 100 and metrics["chat_turns"] > 0:
        insights.append(
            f"Checklist final: {metrics['checklist_done']}/{metrics['checklist_total']} ítems marcados."
        )

    if metrics["probe_regenerations"] > 0:
        insights.append(
            f"Se regeneraron preguntas con IA {metrics['probe_regenerations']} vez/veces durante la sesión."
        )

    if metrics["avg_latency_ms"] is not None:
        insights.append(f"Tiempo medio de respuesta del bot: {metrics['avg_latency_ms']} ms.")

    failed_titles = [BLOCK_TITLES[b["id"]] for b in BLOCK_META if marks.get(b["id"]) == "fail"]
    if failed_titles:
        insights.append("Secciones rechazadas: " + ", ".join(failed_titles) + ".")

    for section in metrics.get("sections", []):
        sid = section["id"]
        mark = section.get("mark", "pending")
        interactions = section.get("interactions", 0)
        title = section.get("title", sid)
        if mark == "pending" and interactions > 0:
            insights.append(
                f"PENDIENTE — {title}: se enviaron {interactions} mensaje(s) vinculado(s) pero aún no se marcó Aprobada/Rechazada."
            )

    return insights


def build_rules_only(session: dict[str, Any]) -> dict[str, Any]:
    """Reglas Fase 0 sin LLM — para refresh automático del panel."""
    return {
        "rules_insights": build_rules_insights(session),
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def _chat_excerpt(chat_log: list[dict], limit: int = 12) -> str:
    lines = []
    for entry in chat_log[-limit:]:
        role = "Abogada" if entry.get("role") == "user" else "Asistente"
        block = entry.get("blockId")
        prefix = f"[{block}] " if block else ""
        text = str(entry.get("text", ""))[:400]
        lines.append(f"{role}{prefix}: {text}")
    return "\n".join(lines)


async def generate_llm_analysis(session: dict[str, Any]) -> tuple[dict[str, Any] | None, str, str]:
    """Returns (analysis, llm_status, llm_message)."""
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            None,
            "skipped_no_key",
            "Análisis IA no disponible (OpenAI no configurada). Las conclusiones por reglas sí están disponibles.",
        )

    metrics = compute_metrics(session)
    marks = session.get("marks") or {}
    chat_log = session.get("chatLog") or []

    if not chat_log and not marks:
        return (
            None,
            "empty",
            "No hay conversación ni marcas suficientes para generar análisis IA.",
        )

    prompt = f"""Analiza esta sesión de prueba Fase 0 de un asistente jurídico colombiano.
La evaluación la hace la abogada manualmente (Aprobada/Rechazada). NO inventes hechos ni sentencias.
Usa SOLO los datos proporcionados.

Métricas: {json.dumps(metrics, ensure_ascii=False)}
Marcas por sección: {json.dumps(marks, ensure_ascii=False)}

Extracto conversación (últimos turnos):
{_chat_excerpt(chat_log)}

Responde JSON:
{{
  "summary": "2-3 oraciones sobre el desempeño general del bot en esta sesión",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": ["acciones concretas para mejorar el bot antes de la siguiente sesión"]
}}
Máximo 4 ítems por lista. Español colombiano, tono profesional."""

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Respondes únicamente JSON válido."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        return (
            {
                "summary": str(data.get("summary", "")).strip(),
                "strengths": [str(s) for s in data.get("strengths", [])[:4]],
                "weaknesses": [str(s) for s in data.get("weaknesses", [])[:4]],
                "recommendations": [str(s) for s in data.get("recommendations", [])[:4]],
            },
            "ok",
            "",
        )
    except Exception as exc:
        logger.warning("Fallo análisis LLM de sesión: %s", exc)
        return (
            None,
            "error",
            "No se pudo generar el análisis IA. Intente de nuevo en unos segundos.",
        )


MARK_LABELS = {
    "pass": "Aprobada",
    "fail": "Rechazada",
    "pending": "Pendiente",
}


async def build_session_report(session: dict[str, Any], include_llm: bool = True) -> dict[str, Any]:
    metrics = compute_metrics(session)
    rules_insights = build_rules_insights(session)
    llm_analysis = None
    llm_status = "empty"
    llm_message = ""
    source = "rules"

    if include_llm:
        llm_analysis, llm_status, llm_message = await generate_llm_analysis(session)
        if llm_analysis:
            source = "llm"
    else:
        llm_status = "skipped_no_key"
        llm_message = "Análisis IA omitido en esta solicitud."

    return {
        "metrics": metrics,
        "rules_insights": rules_insights,
        "llm_analysis": llm_analysis,
        "llm_status": llm_status,
        "llm_message": llm_message,
        "source": source,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def build_export_html(session: dict[str, Any], report: dict[str, Any]) -> str:
    metrics = report.get("metrics") or compute_metrics(session)
    rules = report.get("rules_insights") or build_rules_insights(session)
    llm = report.get("llm_analysis") or {}
    chat_log = session.get("chatLog") or []

    def li(items: list[str]) -> str:
        return "".join(f"<li>{escape(i)}</li>" for i in items)

    llm_block = ""
    if llm:
        llm_block = f"""
<h2>Análisis IA</h2>
<p>{escape(llm.get('summary', ''))}</p>
<h3>Fortalezas</h3><ul>{li(llm.get('strengths', []))}</ul>
<h3>Debilidades</h3><ul>{li(llm.get('weaknesses', []))}</ul>
<h3>Recomendaciones</h3><ul>{li(llm.get('recommendations', []))}</ul>
"""

    mark_notes: dict[str, str] = session.get("markNotes") or {}

    sections_rows = ""
    for s in metrics.get("sections", []):
        mark_label = MARK_LABELS.get(s["mark"], s["mark"])
        note = mark_notes.get(s["id"], "")
        note_cell = f"<br><em>{escape(note)}</em>" if note else ""
        sections_rows += (
            f"<tr><td>{escape(s['title'])}</td>"
            f"<td>{escape(mark_label)}{note_cell}</td>"
            f"<td>{s['points_earned']}/{s['weight']}</td>"
            f"<td>{s['interactions']}</td></tr>"
        )

    transcript = ""
    for entry in chat_log:
        role = "Abogada" if entry.get("role") == "user" else "Asistente"
        transcript += f"<p><strong>{escape(role)}:</strong> {escape(str(entry.get('text', '')))}</p>"

    disclaimer = (
        "<p><em>Borrador analítico — requiere revisión humana. "
        "No constituye dictamen legal.</em></p>"
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Reporte sesión Fase 0</title></head>
<body>
{disclaimer}
<h1>Reporte analítico — Fase 0</h1>
<p>Sesión: {escape(str(session.get('sessionId', '')))}<br>
Inicio: {escape(str(session.get('startedAt', '')))}<br>
Generado: {escape(str(report.get('generated_at', '')))}</p>
<h2>Resumen</h2>
<ul>
<li>Puntaje: {metrics.get('score')}/{metrics.get('total_weight')} ({metrics.get('score_percent')}%)</li>
<li>Duración: {metrics.get('duration_minutes') or '—'} min</li>
<li>Mensajes abogada: {metrics.get('chat_turns')} (probe: {metrics.get('probe_questions')}, manual: {metrics.get('manual_questions')})</li>
<li>Checklist: {metrics.get('checklist_done')}/{metrics.get('checklist_total')}</li>
<li>Latencia media: {metrics.get('avg_latency_ms') or '—'} ms</li>
</ul>
<h2>Secciones</h2>
<table border="1" cellpadding="6"><tr><th>Sección</th><th>Estado</th><th>Puntos</th><th>Interacciones</th></tr>
{sections_rows}</table>
<h2>Conclusiones (reglas)</h2><ul>{li(rules)}</ul>
{llm_block}
<h2>Conversación</h2>
{transcript or '<p>Sin mensajes.</p>'}
</body></html>"""

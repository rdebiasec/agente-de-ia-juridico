"""Guardrails nativos del OpenAI Agents SDK para el POC y especialistas."""

from __future__ import annotations

import re
from typing import Any

from agents import (
    GuardrailFunctionOutput,
    RunContextWrapper,
    ToolGuardrailFunctionOutput,
    ToolInputGuardrailData,
    ToolOutputGuardrailData,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    tool_input_guardrail,
    tool_output_guardrail,
)

from src.agents.guardrails import check_input
from src.agents.pii import mask_pii, pii_flags, sensitive_pii_flags

_OUT_OF_SCOPE_HARD_RE = re.compile(
    r"\b("
    r"divorcio|custodia de menores|alimentos de menor|"
    r"contrato de arrendamiento|sociedad mercantil|"
    r"demanda laboral por despido"
    r")\b",
    re.IGNORECASE,
)
_PENAL_ANCHOR_RE = re.compile(
    r"\b("
    r"penal|v[ií]ctima|ley\s*906|fiscal[ií]a|tutela|"
    r"radicado|audiencia|imputaci[oó]n|denuncia|"
    r"indagaci[oó]n|juicio\s+oral|proceso\s+penal|"
    r"representaci[oó]n\s+de\s+v[ií]ctimas"
    r")\b",
    re.IGNORECASE,
)
_INJECTION_RE = re.compile(
    r"("
    r"ignora\s+(todas\s+)?(las\s+)?instrucciones|"
    r"ignore\s+(all\s+)?(previous\s+)?instructions|"
    r"revela\s+(tu\s+)?(system\s+)?prompt|"
    r"reveal\s+(your\s+)?(system\s+)?prompt|"
    r"desactiva(r)?\s+(los\s+)?guardrails|"
    r"bypass\s+(the\s+)?guardrails|"
    r"olvida\s+(tu\s+)?rol|"
    r"act[uú]a\s+como\s+(si\s+)?no\s+tuvieras\s+l[ií]mites"
    r")",
    re.IGNORECASE,
)
_CITATION_HINT_RE = re.compile(
    r"\b(art\.?\s*\d+|ley\s+\d+|sentencia|radicado\s+\d+|jurisprudencia)\b",
    re.IGNORECASE,
)


def _input_text(value: str | list[TResponseInputItem]) -> str:
    if isinstance(value, str):
        return value
    parts: list[str] = []
    for item in value:
        if isinstance(item, dict):
            content = item.get("content", "")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("text"):
                        parts.append(str(block["text"]))
                    else:
                        parts.append(str(block))
            else:
                parts.append(str(content))
        else:
            parts.append(str(item))
    return "\n".join(parts)


def _user_portion(text: str) -> str:
    """Extrae la consulta del abogado cuando el Runner recibe contexto RAG/plan inyectado."""
    for sep in (
        "[Consulta del despacho]\n",
        "[Consulta del despacho]",
    ):
        if sep in text:
            return text.split(sep, 1)[-1].strip()
    for marker in (
        "[Base de conocimiento — fragmentos relevantes]",
        "[Expediente del caso]",
        "[Expediente]",
    ):
        if marker in text:
            tail = text.rsplit("\n\n", 1)[-1].strip()
            if tail and not tail.startswith("["):
                return tail
    return text.strip()


def _turn_text(data: ToolInputGuardrailData) -> str:
    ctx = data.context
    chunks: list[str] = [str(getattr(ctx, "tool_arguments", "") or "")]
    turn_input = getattr(ctx, "turn_input", None) or []
    for item in turn_input:
        if isinstance(item, dict):
            content = item.get("content", "")
            if isinstance(content, str):
                chunks.append(content)
            else:
                chunks.append(str(content))
        else:
            chunks.append(str(item))
    return "\n".join(chunks)


@input_guardrail(name="poc_input_guardrail", run_in_parallel=False)
async def poc_input_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """Bloquea entradas invalidas, injection o fuera de alcance sin ancla penal."""
    full = _input_text(input).strip()
    text = _user_portion(full)
    anchors_found = bool(_PENAL_ANCHOR_RE.search(text))
    oos_matched = bool(_OUT_OF_SCOPE_HARD_RE.search(text))

    ok, err = check_input(text)
    if not ok:
        return GuardrailFunctionOutput(
            output_info={
                "reason": err or "entrada_invalida",
                "anchors_found": anchors_found,
                "oos_matched": oos_matched,
            },
            tripwire_triggered=True,
        )
    if not text:
        return GuardrailFunctionOutput(
            output_info={
                "reason": "entrada_vacia",
                "anchors_found": False,
                "oos_matched": False,
            },
            tripwire_triggered=True,
        )
    if _INJECTION_RE.search(text):
        return GuardrailFunctionOutput(
            output_info={
                "reason": "injection_suspect",
                "anchors_found": anchors_found,
                "oos_matched": oos_matched,
            },
            tripwire_triggered=True,
        )
    hard_oos = oos_matched and not anchors_found
    return GuardrailFunctionOutput(
        output_info={
            "reason": "fuera_de_alcance" if hard_oos else "ok",
            "anchors_found": anchors_found,
            "oos_matched": oos_matched,
        },
        tripwire_triggered=hard_oos,
    )


@output_guardrail(name="poc_output_guardrail")
async def poc_output_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    output: Any,
) -> GuardrailFunctionOutput:
    """Tripwire solo para salida vacía; la PII se minimiza después del run.

    Email y teléfono pueden ser datos operativos legítimos. Documento,
    dirección y nombres protegidos se enmascaran en `apply_output_guardrails`
    salvo que el flujo haya sido aprobado.
    """
    text = (output if isinstance(output, str) else str(output or "")).strip()
    empty = not text
    flags = [] if empty else pii_flags(text)
    invention_suspect = (not empty) and citation_hints_without_pending(text)
    pending_markers_count = text.count("[PENDIENTE") if text else 0
    if empty:
        reason = "salida_vacia"
        trip = True
    else:
        reason = "sensitive_pii_pending_mask" if sensitive_pii_flags(text) else "ok"
        trip = False
    # Soft flags only: invention_suspect no dispara tripwire (el abogado revisa).
    # has_disclaimer se mide en _finalize_trace sobre el texto ya post-procesado.
    return GuardrailFunctionOutput(
        output_info={
            "reason": reason,
            "chars": len(text),
            "pii_flags": flags,
            "invention_suspect": invention_suspect,
            "pending_markers_count": pending_markers_count,
        },
        tripwire_triggered=trip,
    )


def _structured_text(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output.strip()
    if hasattr(output, "model_dump"):
        data = output.model_dump()
        for key in (
            "cuerpo",
            "fundamentos",
            "resumen",
            "hipotesis_tipica",
            "titulo",
            "veredicto",
        ):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        return str(data).strip()
    return str(output).strip()


@output_guardrail(name="specialist_output_guardrail")
async def specialist_output_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    output: Any,
) -> GuardrailFunctionOutput:
    """Output guardrail genérico de especialistas (vacío + PII flags)."""
    text = _structured_text(output)
    flags = pii_flags(text) if text else []
    empty = not text
    trip = empty
    return GuardrailFunctionOutput(
        output_info={
            "reason": (
                "salida_vacia"
                if empty
                else ("sensitive_pii_pending_policy" if sensitive_pii_flags(text) else "ok")
            ),
            "chars": len(text),
            "pii_flags": flags,
            "agent": getattr(agent, "name", None),
        },
        tripwire_triggered=trip,
    )


@output_guardrail(name="redactor_output_guardrail")
async def redactor_output_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    output: Any,
) -> GuardrailFunctionOutput:
    """Redactor: exige cuerpo no vacío; marca citas sin pendiente."""
    text = _structured_text(output)
    empty = not text
    missing_pending = (not empty) and citation_hints_without_pending(text)
    trip = empty
    return GuardrailFunctionOutput(
        output_info={
            "reason": "salida_vacia" if empty else ("citas_sin_pendiente" if missing_pending else "ok"),
            "chars": len(text),
            "pii_flags": pii_flags(text) if text else [],
            "citation_without_pending": missing_pending,
            "agent": getattr(agent, "name", None),
        },
        tripwire_triggered=trip,
    )



@output_guardrail(name="calidad_output_guardrail")
async def calidad_output_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    output: Any,
) -> GuardrailFunctionOutput:
    """Calidad: exige veredicto DictamenCalidad reconocible."""
    veredicto = None
    if hasattr(output, "model_dump"):
        veredicto = (output.model_dump() or {}).get("veredicto")
    elif isinstance(output, dict):
        veredicto = output.get("veredicto")
    text = _structured_text(output)
    valid = veredicto in ("aprobable", "con_cambios", "rechazado", "escalar")
    empty = not text and not valid
    trip = empty or not valid
    return GuardrailFunctionOutput(
        output_info={
            "reason": "salida_vacia" if empty else ("veredicto_invalido" if not valid else "ok"),
            "veredicto": veredicto,
            "chars": len(text),
            "agent": getattr(agent, "name", None),
        },
        tripwire_triggered=trip,
    )


@tool_input_guardrail(name="poc_tool_input_guardrail")
def poc_tool_input_guardrail(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Bloquea routing ilegal, PII sensible y payloads excesivos."""
    tool_name = getattr(data.context, "tool_name", "") or ""
    blob = _turn_text(data)
    if len(blob) > 12000:
        return ToolGuardrailFunctionOutput.reject_content(
            message=(
                "El pedido interno a la tool es demasiado largo. "
                "Resuma hechos, etapa y pedido concreto antes de consultar al equipo."
            ),
            output_info={
                "reason": "payload_too_large",
                "tool_name": tool_name,
                "chars": len(blob),
            },
        )
    flags = sensitive_pii_flags(blob)
    if flags:
        return ToolGuardrailFunctionOutput.reject_content(
            message=(
                "No invoque esa tool con PII sensible (documento, dirección o nombre "
                "etiquetado de víctima/menor). "
                "Reformule el pedido interno sin datos sensibles innecesarios."
            ),
            output_info={"reason": "pii_in_args", "tool_name": tool_name, "pii_flags": flags},
        )
    if tool_name == "redactor_documentos_juridicos" and re.search(
        r"\b(tutela|acci[oó]n\s+de\s+tutela)\b", blob, re.I
    ):
        return ToolGuardrailFunctionOutput.reject_content(
            message=(
                "Routing bloqueado: la acción de tutela está fuera del producto. "
                "Reformule el pedido como memorial de impulso, derecho de petición "
                "o seguimiento procesal penal."
            ),
            output_info={"reason": "blocked_routing_tutela_out_of_scope", "tool_name": tool_name},
        )
    return ToolGuardrailFunctionOutput.allow(
        output_info={"reason": "ok", "tool_name": tool_name}
    )


@tool_output_guardrail(name="poc_tool_output_guardrail")
def poc_tool_output_guardrail(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Si el especialista devuelve PII, rechaza el contenido y pide reformulacion."""
    tool_name = getattr(data.context, "tool_name", "") or ""
    raw = data.output
    text = raw if isinstance(raw, str) else str(raw or "")
    flags = sensitive_pii_flags(text)
    if flags:
        return ToolGuardrailFunctionOutput.reject_content(
            message=(
                f"La tool `{tool_name}` devolvio PII etiquetada. "
                f"Resumen enmascarado: {mask_pii(text)[:500]}"
            ),
            output_info={"reason": "pii_in_tool_output", "tool_name": tool_name, "pii_flags": flags},
        )
    return ToolGuardrailFunctionOutput.allow(
        output_info={"reason": "ok", "tool_name": tool_name, "chars": len(text)}
    )


def poc_input_guardrails() -> list:
    return [poc_input_guardrail]


def poc_output_guardrails() -> list:
    return [poc_output_guardrail]


def specialist_output_guardrails() -> list:
    return [specialist_output_guardrail]


def redactor_output_guardrails() -> list:
    return [redactor_output_guardrail]



def calidad_output_guardrails() -> list:
    return [calidad_output_guardrail]


def poc_tool_input_guardrails() -> list:
    return [poc_tool_input_guardrail]


def poc_tool_output_guardrails() -> list:
    return [poc_tool_output_guardrail]


def citation_hints_without_pending(text: str) -> bool:
    """True si hay indicios de citas/radicados sin marca de pendiente."""
    if not text:
        return False
    if "[PENDIENTE DE VERIFICAR]" in text or "[PENDIENTE]" in text:
        return False
    return bool(_CITATION_HINT_RE.search(text))

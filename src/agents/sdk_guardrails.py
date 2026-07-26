"""Guardrails nativos del OpenAI Agents SDK para el POC."""

from __future__ import annotations

import re
from typing import Any

from agents import (
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)

from src.agents.guardrails import check_input

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
# Cédula colombiana típica / email / teléfono — señales de PII en salida.
_PII_RE = re.compile(
    r"("
    r"\b\d{6,10}\b|"  # documento numérico largo
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
    r"\b(?:\+?57[\s-]?)?(?:3\d{2}|60\d)[\s-]?\d{3}[\s-]?\d{4}\b"
    r")",
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
    # Chat path: contexto + mensaje crudo al final.
    for marker in ("[Base de conocimiento — fragmentos relevantes]", "[Expediente del caso]", "[Expediente]"):
        if marker in text:
            # último bloque tras el contexto suele ser el mensaje
            tail = text.rsplit("\n\n", 1)[-1].strip()
            if tail and not tail.startswith("["):
                return tail
    return text.strip()


def _pii_flags(text: str) -> list[str]:
    flags: list[str] = []
    if re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I):
        flags.append("email")
    if re.search(r"\b(?:\+?57[\s-]?)?(?:3\d{2}|60\d)[\s-]?\d{3}[\s-]?\d{4}\b", text):
        flags.append("phone")
    # Documento solo si aparece etiquetado (evita falsos positivos con radicados).
    if re.search(r"\b(c[eé]dula|cc|nit|documento\s+de\s+identidad)\b.{0,20}\d{6,10}", text, re.I):
        flags.append("document_id")
    return flags


@input_guardrail(name="poc_input_guardrail", run_in_parallel=False)
async def poc_input_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """Bloquea entradas inválidas, injection o fuera de alcance sin ancla penal."""
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
    """Tripwire si salida vacía o con PII etiquetada (cédula/email/teléfono)."""
    text = (output if isinstance(output, str) else str(output or "")).strip()
    empty = not text
    flags = [] if empty else _pii_flags(text)
    if empty:
        reason = "salida_vacia"
        trip = True
    elif flags:
        reason = "pii_detected"
        trip = True
    else:
        reason = "ok"
        trip = False
    return GuardrailFunctionOutput(
        output_info={
            "reason": reason,
            "chars": len(text),
            "pii_flags": flags,
            "has_disclaimer": "Borrador informativo" in text,
        },
        tripwire_triggered=trip,
    )


def poc_input_guardrails() -> list:
    return [poc_input_guardrail]


def poc_output_guardrails() -> list:
    return [poc_output_guardrail]

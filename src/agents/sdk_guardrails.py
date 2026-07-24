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
    r"radicado|audiencia|imputaci[oó]n|denuncia"
    r")\b",
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


@input_guardrail(name="poc_input_guardrail", run_in_parallel=False)
async def poc_input_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """Bloquea entradas inválidas o claramente fuera de alcance sin ancla penal."""
    full = _input_text(input).strip()
    text = _user_portion(full)
    ok, err = check_input(text)
    if not ok:
        return GuardrailFunctionOutput(
            output_info={"reason": err or "entrada_invalida"},
            tripwire_triggered=True,
        )
    if not text:
        return GuardrailFunctionOutput(
            output_info={"reason": "entrada_vacia"},
            tripwire_triggered=True,
        )
    hard_oos = bool(_OUT_OF_SCOPE_HARD_RE.search(text)) and not bool(_PENAL_ANCHOR_RE.search(text))
    return GuardrailFunctionOutput(
        output_info={"reason": "fuera_de_alcance" if hard_oos else "ok"},
        tripwire_triggered=hard_oos,
    )


@output_guardrail(name="poc_output_guardrail")
async def poc_output_guardrail(
    ctx: RunContextWrapper[Any],
    agent: Any,
    output: Any,
) -> GuardrailFunctionOutput:
    """Dispara tripwire si la salida final del POC está vacía."""
    text = (output if isinstance(output, str) else str(output or "")).strip()
    empty = not text
    return GuardrailFunctionOutput(
        output_info={"reason": "salida_vacia" if empty else "ok", "chars": len(text)},
        tripwire_triggered=empty,
    )


def poc_input_guardrails() -> list:
    return [poc_input_guardrail]


def poc_output_guardrails() -> list:
    return [poc_output_guardrail]

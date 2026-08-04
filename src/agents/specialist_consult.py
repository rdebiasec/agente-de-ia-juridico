"""Input estructurado para especialistas invocados via Agent.as_tool (G2)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ConsultModo = Literal["inicial", "repregunta", "contraste"]


class SpecialistConsultInput(BaseModel):
    """Contrato tipado que el Gerente pasa al equipo interno."""

    pedido: str = Field(
        ...,
        description="Pedido concreto al especialista (una tarea acotada).",
    )
    hechos_confirmados: str = Field(
        default="",
        description="Hechos ya confirmados del expediente (no inferencias).",
    )
    etapa: str = Field(
        default="",
        description="Etapa procesal aparente (indagación, imputación, etc.).",
    )
    restricciones: str = Field(
        default="",
        description="Límites: no inventar, PII a omitir, alcance del paso.",
    )
    objetivo_deliberacion: str = Field(
        default="",
        description="Decisión del Gerente que depende de esta consulta (razonamiento breve).",
    )
    contexto_previo: str = Field(
        default="",
        description="Resumen de hallazgos previos del mismo turno (para repregunta o contraste).",
    )
    ronda: int = Field(
        default=1,
        ge=1,
        description="Número de ronda de deliberación en este turno (1..N).",
    )
    modo: ConsultModo = Field(
        default="inicial",
        description="inicial | repregunta | contraste.",
    )


def specialist_input_builder(options: dict[str, Any]) -> str:
    """Render compacto en español para el nested agent (sin volcar JSON Schema)."""
    params = options.get("params")
    if hasattr(params, "model_dump"):
        data = params.model_dump()
    elif isinstance(params, dict):
        data = params
    else:
        data = {"pedido": str(params or "")}

    lines = [
        "Consulta interna del Coordinador del Caso (backoffice).",
        f"Pedido: {(data.get('pedido') or '').strip()}",
    ]
    hechos = (data.get("hechos_confirmados") or "").strip()
    etapa = (data.get("etapa") or "").strip()
    restricciones = (data.get("restricciones") or "").strip()
    objetivo = (data.get("objetivo_deliberacion") or "").strip()
    contexto = (data.get("contexto_previo") or "").strip()
    modo = str(data.get("modo") or "inicial").strip() or "inicial"
    try:
        ronda = int(data.get("ronda") or 1)
    except (TypeError, ValueError):
        ronda = 1
    if hechos:
        lines.append(f"Hechos confirmados: {hechos}")
    if etapa:
        lines.append(f"Etapa: {etapa}")
    if restricciones:
        lines.append(f"Restricciones: {restricciones}")
    if objetivo:
        lines.append(f"Objetivo de deliberación: {objetivo}")
    if contexto:
        lines.append(f"Contexto previo (misma junta): {contexto}")
    lines.append(f"Ronda: {max(1, ronda)} · Modo: {modo}")
    lines.append(
        "Devuelve hallazgos operativos claros; marca [PENDIENTE DE VERIFICAR] lo no soportado."
    )
    lines.append(
        "Cierra con bloques: objeciones_o_riesgos, preguntas_al_gerente (0–3), "
        "confianza (baja|media|alta)."
    )
    return "\n".join(lines)


def consult_fields_from_raw(raw: Any) -> dict[str, str]:
    """Extrae campos de deliberación desde tool_arguments (JSON o texto)."""
    data: dict[str, Any] = {}
    if isinstance(raw, str) and raw.strip():
        import json

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                data = parsed
        except Exception:
            return {"pedido": raw.strip(), "objetivo_deliberacion": "", "modo": "inicial"}
    elif isinstance(raw, dict):
        data = raw
    elif hasattr(raw, "model_dump"):
        data = raw.model_dump()

    return {
        "pedido": str(data.get("pedido") or "").strip(),
        "hechos_confirmados": str(data.get("hechos_confirmados") or "").strip(),
        "etapa": str(data.get("etapa") or "").strip(),
        "restricciones": str(data.get("restricciones") or "").strip(),
        "objetivo_deliberacion": str(data.get("objetivo_deliberacion") or "").strip(),
        "contexto_previo": str(data.get("contexto_previo") or "").strip(),
        "modo": str(data.get("modo") or "inicial").strip() or "inicial",
        "ronda": str(data.get("ronda") or "").strip(),
    }

"""Input estructurado para especialistas invocados via Agent.as_tool (G2)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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
        "Consulta interna del Gerente del Caso (backoffice).",
        f"Pedido: {(data.get('pedido') or '').strip()}",
    ]
    hechos = (data.get("hechos_confirmados") or "").strip()
    etapa = (data.get("etapa") or "").strip()
    restricciones = (data.get("restricciones") or "").strip()
    if hechos:
        lines.append(f"Hechos confirmados: {hechos}")
    if etapa:
        lines.append(f"Etapa: {etapa}")
    if restricciones:
        lines.append(f"Restricciones: {restricciones}")
    lines.append(
        "Devuelve hallazgos operativos claros; marca [PENDIENTE DE VERIFICAR] lo no soportado."
    )
    return "\n".join(lines)

"""Evaluación determinista de urgencia penal (skill detectar_urgencia_penal)."""

from __future__ import annotations

import re
import time
from typing import Literal

from pydantic import BaseModel, Field

from src.storage.models import Expediente

UrgencyLevel = Literal["critica", "alta", "media", "baja"]

_CRITICA_RE = re.compile(
    r"\b("
    r"amenaza\s+(de\s+)?(muerte|integridad)|riesgo\s+(a\s+)?(la\s+)?vida|"
    r"violencia\s+inminente|intento\s+de\s+(homicidio|feminicidio)|"
    r"captura\s+inminente|libertad\s+inmediata|"
    r"destrucci[oó]n\s+(inminente\s+)?(de\s+)?(prueba|evidencia)|"
    r"audiencia\s+(hoy|esta\s+ma[nñ]ana)|vence\s+hoy|vencimiento\s+hoy|"
    r"t[eé]rmino\s+vence\s+hoy"
    r")\b",
    re.I,
)
_ALTA_RE = re.compile(
    r"\b("
    r"urgente|urgencia|inminente|"
    r"audiencia\s+(ma[nñ]ana|pasado\s+ma[nñ]ana|pr[oó]xima)|"
    r"vencimiento|vence\s+(ma[nñ]ana|esta\s+semana)|"
    r"t[eé]rmino\s+(procesal|pr[oó]ximo|por\s+vencer)|"
    r"prescripci[oó]n|caducidad|"
    r"medida\s+de\s+protecci[oó]n|riesgo\s+para\s+la\s+v[ií]ctima|"
    r"p[eé]rdida\s+(de\s+)?(prueba|evidencia)|preservar\s+evidencia"
    r")\b",
    re.I,
)
_MEDIA_RE = re.compile(
    r"\b("
    r"pronto|esta\s+semana|priorizar|prioridad|"
    r"inactividad|sin\s+movimiento|demora\s+procesal|"
    r"seguimiento\s+urgente|revisar\s+t[eé]rminos?"
    r")\b",
    re.I,
)


class UrgencyResult(BaseModel):
    """Contrato de detectar_urgencia_penal (código, no function_tool)."""

    nivel_urgencia: UrgencyLevel = Field(
        default="baja",
        description="Nivel de urgencia preliminar del turno.",
    )
    motivos: list[str] = Field(default_factory=list)
    accion_inmediata_sugerida: str = Field(default="")
    escalar_humano: bool = Field(
        default=False,
        description="True cuando nivel es critica o alta.",
    )
    evaluada_en: int = Field(
        default_factory=lambda: int(time.time()),
        description="Unix timestamp de la evaluación.",
    )

    @property
    def urgencia_preliminar(self) -> bool:
        return self.nivel_urgencia in {"critica", "alta"}


def assess_urgency(
    message: str,
    expediente: Expediente | None = None,
) -> UrgencyResult:
    """Clasifica urgencia determinista (sin LLM)."""
    text = (message or "").strip()
    lower = text.lower()
    motivos: list[str] = []
    now = int(time.time())

    if _CRITICA_RE.search(text):
        motivos.append("Indicios de riesgo crítico reportados en el turno.")
        action = (
            "Escalar al abogado titular de inmediato; verificar integridad, "
            "términos del día y preservación de evidencia."
        )
        return UrgencyResult(
            nivel_urgencia="critica",
            motivos=motivos,
            accion_inmediata_sugerida=action,
            escalar_humano=True,
            evaluada_en=now,
        )

    if _ALTA_RE.search(text):
        if any(k in lower for k in ("vencimiento", "vence", "término", "termino")):
            motivos.append("Mención de vencimiento o término procesal.")
        if "audiencia" in lower:
            motivos.append("Audiencia próxima o con carácter urgente.")
        if any(k in lower for k in ("urgente", "urgencia", "inminente")):
            motivos.append("El despacho marcó el turno como urgente.")
        if any(k in lower for k in ("protección", "proteccion", "víctima", "victima", "evidencia")):
            motivos.append("Riesgo a víctima o a material probatorio.")
        if not motivos:
            motivos.append("Señales de urgencia alta en el texto del turno.")
        return UrgencyResult(
            nivel_urgencia="alta",
            motivos=motivos,
            accion_inmediata_sugerida=(
                "Confirmar con el abogado titular antes del análisis de fondo; "
                "priorizar verificación de términos y actuaciones inminentes."
            ),
            escalar_humano=True,
            evaluada_en=now,
        )

    if _MEDIA_RE.search(text):
        motivos.append("Prioridad operativa o inactividad procesal reportada.")
        return UrgencyResult(
            nivel_urgencia="media",
            motivos=motivos,
            accion_inmediata_sugerida=(
                "Continuar triage y seguimiento; no requiere escalamiento inmediato."
            ),
            escalar_humano=False,
            evaluada_en=now,
        )

    # Señales suaves desde expediente (términos abiertos sin fecha = pendiente).
    if expediente and expediente.terminos:
        open_terms = [
            t
            for t in expediente.terminos
            if str(t.get("estado", "")).lower() in {"", "abierto", "pendiente", "activo"}
        ]
        if open_terms:
            motivos.append(
                "[PENDIENTE DE VERIFICAR] Hay términos en expediente sin evaluación de vencimiento."
            )
            return UrgencyResult(
                nivel_urgencia="media",
                motivos=motivos,
                accion_inmediata_sugerida=(
                    "Verificar fechas de términos del expediente con el abogado."
                ),
                escalar_humano=False,
                evaluada_en=now,
            )

    return UrgencyResult(
        nivel_urgencia="baja",
        motivos=[],
        accion_inmediata_sugerida="Continuar flujo normal del Gerente del Caso.",
        escalar_humano=False,
        evaluada_en=now,
    )


def format_escalation_notice(urgency: UrgencyResult) -> str:
    """Mensaje corto de escalamiento (sin PII innecesaria)."""
    motivos = "; ".join(urgency.motivos) if urgency.motivos else "riesgo procesal reportado"
    return (
        f"[ESCALAMIENTO URGENCIA {urgency.nivel_urgencia.upper()}] "
        f"{motivos}. Acción sugerida: {urgency.accion_inmediata_sugerida} "
        "Requiere confirmación del abogado titular antes de actuaciones externas."
    )

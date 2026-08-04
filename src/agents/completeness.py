"""Gate determinista de completitud para el loop del Coordinador del Caso."""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Literal

from src.storage.models import Expediente

POC_AGENT_ID = "coordinador_caso"

_HIGH_RISK_DESTINATIONS = {
    "redactor_documentos_juridicos",
}
_FACT_RE = re.compile(
    r"\b(ocurri[oó]|sucedi[oó]|denunci[éeó]|agredi[oó]|amenaz[óo]|hurt[óo]|"
    r"fiscal[ií]a|audiencia|captur[ao]|imput[óo]|víctima|victima|hechos?)\b",
    re.I,
)
_POWER_RE = re.compile(
    r"\b(poder\s+(?:adjunto|aportado|firmado|otorgado)|tengo\s+(?:el\s+)?poder|"
    r"apoderad[oa]\s+(?:reconocid[oa]|designad[oa]))\b",
    re.I,
)
_LAST_ACTION_RE = re.compile(
    r"\b([uú]ltima\s+actuaci[oó]n|[uú]ltimo\s+auto|[uú]ltima\s+audiencia|"
    r"audiencia\s+de|imputaci[oó]n|acusaci[oó]n|archivo|preclusi[oó]n|"
    r"traslado|sentencia|fallo|notificad[oa])\b",
    re.I,
)
_STAGE_RE = re.compile(
    r"\b(indagaci[oó]n|investigaci[oó]n|imputaci[oó]n|acusaci[oó]n|juicio|"
    r"ejecuci[oó]n)\b",
    re.I,
)
_OPERATIONAL_RE = re.compile(
    r"\b(redact|proyect|prepar|elabor|analiz|eval[uú]|seguimiento|cronolog|"
    r"tipicidad|ruta\s+procesal|estrateg|riesgo|audiencia|memorial|"
    r"recurso|informe|impulso|vac[ií]os?\s+probatorios?)\w*",
    re.I,
)

FaltantePrioridad = Literal["bloqueante", "deseable"]
PendienteTipo = Literal["hecho", "cita", "radicado", "fecha", "otro"]
PendienteImpacto = Literal["alto", "medio", "bajo"]

# Checklist documental real del gate (labels canónicos → motivo).
_CHECKLIST_MOTIVOS: dict[str, str] = {
    "hechos mínimos del caso": "Sin hechos mínimos no se puede analizar ni redactar con soporte.",
    "número de radicado": "Alto riesgo: memorial/seguimiento requieren radicado verificable.",
    "poder o calidad en que actúa el despacho": (
        "Alto riesgo: falta acreditar poder o rol del despacho."
    ),
    "última actuación procesal": "Necesaria para ubicar oportunidad y no actuar a ciegas.",
    "partes relevantes": "Identificar víctima/procesado/agresor evita piezas incompletas.",
    "etapa o última actuación procesal": (
        "Ruta 906 / audiencia / seguimiento requieren etapa o última actuación."
    ),
}


@dataclass(frozen=True)
class FaltanteItem:
    elemento: str
    prioridad: FaltantePrioridad = "bloqueante"
    motivo: str = ""
    responsable_sugerido: str = "abogado_titular"


@dataclass(frozen=True)
class CompletenessResult:
    puede_continuar: bool
    faltantes_detalle: list[FaltanteItem] = field(default_factory=list)
    hechos_minimos: bool = False
    poder_acreditado: bool = False
    ultima_actuacion: bool = False
    etapa_aparente: str = "desconocida"

    @property
    def faltantes(self) -> list[str]:
        """Compat: labels string para ledger / mensajes / TriageResult."""
        return [item.elemento for item in self.faltantes_detalle]


def _faltante(elemento: str, *, prioridad: FaltantePrioridad = "bloqueante") -> FaltanteItem:
    return FaltanteItem(
        elemento=elemento,
        prioridad=prioridad,
        motivo=_CHECKLIST_MOTIVOS.get(elemento, "Dato requerido por el gate de completitud."),
        responsable_sugerido="abogado_titular",
    )


def infer_stage(text: str, expediente: Expediente | None = None) -> str:
    current = (expediente.etapa_actual if expediente else None) or ""
    combined = f"{current}\n{text}".lower()
    if "indagaci" in combined:
        return "indagacion"
    if "investigaci" in combined:
        return "investigacion"
    if "imputaci" in combined:
        return "imputacion"
    if "juicio" in combined or "acusaci" in combined:
        return "juicio"
    if "ejecuci" in combined or "sentencia" in combined:
        return "ejecucion"
    return "desconocida"


def assess_completeness(
    text: str,
    *,
    destination: str,
    expediente: Expediente | None = None,
) -> CompletenessResult:
    """Evalúa mínimos por riesgo sin pedir datos innecesarios para una consulta inicial."""
    exp = expediente or Expediente(session_id="")
    combined = (text or "").strip()
    if destination == POC_AGENT_ID or not _OPERATIONAL_RE.search(combined):
        return CompletenessResult(
            puede_continuar=True,
            faltantes_detalle=[],
            hechos_minimos=bool(exp.hechos_minimos_confirmados),
            poder_acreditado=bool(exp.poder_acreditado),
            ultima_actuacion=bool(exp.ultima_actuacion_confirmada),
            etapa_aparente=infer_stage(combined, exp),
        )
    facts = bool(exp.hechos_minimos_confirmados or (_FACT_RE.search(combined) and len(combined) >= 55))
    power = bool(exp.poder_acreditado or _POWER_RE.search(combined))
    last_action = bool(exp.ultima_actuacion_confirmada or _LAST_ACTION_RE.search(combined))
    stage = infer_stage(combined, exp)
    has_stage = bool(exp.etapa_actual or _STAGE_RE.search(combined))
    has_parties = bool(exp.partes) or bool(
        re.search(r"\b(accionante|accionado|denunciante|indiciado|procesado|víctima|victima)\b", combined, re.I)
    )

    required: list[tuple[str, bool]] = [("hechos mínimos del caso", facts)]
    if destination in _HIGH_RISK_DESTINATIONS:
        required.extend(
            [
                ("número de radicado", bool(exp.radicado)),
                ("poder o calidad en que actúa el despacho", power or bool(exp.rol_despacho)),
                ("última actuación procesal", last_action),
                ("partes relevantes", has_parties),
            ]
        )
    elif destination in {
        "analista_audiencias",
        "analista_seguimiento_procesal",
        "analista_ruta_procesal",
    }:
        required.extend(
            [
                ("número de radicado", bool(exp.radicado)),
                ("etapa o última actuación procesal", has_stage or last_action),
            ]
        )

    detalle = [_faltante(label) for label, present in required if not present]
    return CompletenessResult(
        puede_continuar=not detalle,
        faltantes_detalle=detalle,
        hechos_minimos=facts,
        poder_acreditado=power,
        ultima_actuacion=last_action,
        etapa_aparente=stage,
    )


def format_missing_request(faltantes: list[str]) -> str:
    items = "\n".join(f"- {item}" for item in faltantes)
    return (
        "Antes de delegar o preparar una actuación, necesito completar el expediente con:\n"
        f"{items}\n\n"
        "Envíeme esos datos o documentos y volveré a verificar el caso."
    )


def persist_verification(
    expediente: Expediente,
    result: CompletenessResult,
    *,
    destination: str,
    urgency: dict | None = None,
) -> Expediente:
    """Actualiza ledger y métricas; las tareas se cierran cuando llega el dato."""
    now = int(time.time())
    from src.storage import get_repository

    def _apply(current: Expediente) -> None:
        previous = {
            str(task.get("titulo")): task
            for task in current.tareas_gerencia
            if task.get("tipo") == "faltante"
        }
        tasks: list[dict] = [
            task for task in current.tareas_gerencia if task.get("tipo") != "faltante"
        ]
        for title, old in previous.items():
            if title not in result.faltantes:
                tasks.append({**old, "estado": "cerrada", "cerrada_en": now})
        for item in result.faltantes_detalle:
            title = item.elemento
            old = previous.get(title, {})
            tasks.append(
                {
                    "id": old.get("id")
                    or f"faltante-{hashlib.sha256(title.encode()).hexdigest()[:10]}",
                    "tipo": "faltante",
                    "titulo": title,
                    "responsable": item.responsable_sugerido,
                    "estado": "pendiente",
                    "prioridad": item.prioridad,
                    "motivo": item.motivo,
                    "creada_en": old.get("creada_en") or now,
                }
            )
        metrics = dict(current.metricas_gerencia or {})
        metrics["verificaciones"] = int(metrics.get("verificaciones", 0)) + 1
        metric = (
            "bloqueos_por_faltantes"
            if result.faltantes
            else "verificaciones_aprobadas"
        )
        metrics[metric] = int(metrics.get(metric, 0)) + 1
        metrics["ultimo_destino_evaluado"] = destination
        metrics["ultima_verificacion_en"] = now
        if urgency:
            metrics["ultima_urgencia"] = urgency
        current.faltantes_gerencia = list(result.faltantes)
        current.tareas_gerencia = tasks
        current.metricas_gerencia = metrics
        current.hechos_minimos_confirmados = (
            current.hechos_minimos_confirmados or result.hechos_minimos
        )
        current.poder_acreditado = current.poder_acreditado or result.poder_acreditado
        current.ultima_actuacion_confirmada = (
            current.ultima_actuacion_confirmada or result.ultima_actuacion
        )
        current.actualizado_en = time.time()

    return get_repository().mutate_expediente(expediente.session_id, _apply)


def _classify_pending(text: str) -> tuple[PendienteTipo, PendienteImpacto]:
    lower = text.lower()
    if re.search(r"\b(radicado|n[uú]mero\s+de\s+proceso)\b", lower):
        return "radicado", "alto"
    if re.search(r"\b(art[ií]culo|ley|sentencia|jurisprudencia|norma)\b", lower):
        return "cita", "alto"
    if re.search(r"\b(fecha|audiencia|vencimiento|t[eé]rmino|plazo)\b", lower):
        return "fecha", "alto"
    if re.search(r"\b(hecho|relato|ocurri|denunci)\b", lower):
        return "hecho", "medio"
    return "otro", "medio"


def record_specialist_result(
    session_id: str,
    *,
    agent_id: str,
    text: str,
    status: str,
) -> dict:
    """Registra delegación y pendientes explícitos devueltos por especialistas."""
    from src.storage import get_repository

    repo = get_repository()
    pending: list[dict] = []
    for line in (text or "").splitlines():
        if re.search(r"\[(?:PENDIENTE(?:\s+DE\s+VERIFICAR)?|FALTANTE)\]", line, re.I):
            cleaned = re.sub(r"\[[^\]]+\]\s*:?\s*", "", line).strip(" -*")
            if cleaned:
                tipo, impacto = _classify_pending(cleaned)
                pending.append(
                    {
                        "elemento": cleaned[:240],
                        "tipo": tipo,
                        "impacto_juridico": impacto,
                    }
                )

    now = int(time.time())

    def _apply(expediente: Expediente) -> None:
        metrics = dict(expediente.metricas_gerencia or {})
        if agent_id != POC_AGENT_ID:
            metrics["delegaciones"] = int(metrics.get("delegaciones", 0)) + 1
            if status != "done":
                metrics["delegaciones_bloqueadas"] = int(
                    metrics.get("delegaciones_bloqueadas", 0)
                ) + 1
        metrics["ultimo_especialista"] = agent_id
        existing = {
            str(task.get("titulo")): task for task in expediente.tareas_gerencia
        }
        for item in pending:
            title = item["elemento"]
            existing[title] = {
                **existing.get(title, {}),
                "id": existing.get(title, {}).get("id")
                or f"pendiente-{hashlib.sha256(title.encode()).hexdigest()[:10]}",
                "tipo": "verificacion_especialista",
                "titulo": title,
                "responsable": "abogado_titular",
                "origen": agent_id,
                "estado": "pendiente",
                "pendiente_tipo": item["tipo"],
                "impacto_juridico": item["impacto_juridico"],
                "creada_en": existing.get(title, {}).get("creada_en") or now,
            }
        expediente.tareas_gerencia = list(existing.values())
        expediente.metricas_gerencia = metrics
        expediente.actualizado_en = time.time()

    repo.mutate_expediente(session_id, _apply)
    return {
        "faltantes_detectados": [p["elemento"] for p in pending],
        "pendientes_detalle": pending,
        "responsable_verificacion": "abogado_titular" if pending else None,
    }

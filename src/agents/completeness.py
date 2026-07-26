"""Gate determinista de completitud para el loop del Gerente del Caso Penal."""

from __future__ import annotations

import re
from dataclasses import dataclass
import hashlib
import time

from src.storage.models import Expediente

POC_AGENT_ID = "coordinador_expediente_penal"

_HIGH_RISK_DESTINATIONS = {
    "redactor_documentos_juridicos_penales",
    "evaluador_derechos_fundamentales_tutela",
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
    r"ejecuci[oó]n|tutela\s+en\s+preparaci[oó]n)\b",
    re.I,
)
_OPERATIONAL_RE = re.compile(
    r"\b(redact|proyect|prepar|elabor|analiz|eval[uú]|seguimiento|cronolog|"
    r"tipicidad|ruta\s+procesal|estrateg|riesgo|audiencia|tutela|memorial|"
    r"recurso|informe|impulso|vac[ií]os?\s+probatorios?)\w*",
    re.I,
)


@dataclass(frozen=True)
class CompletenessResult:
    puede_continuar: bool
    faltantes: list[str]
    hechos_minimos: bool
    poder_acreditado: bool
    ultima_actuacion: bool
    etapa_aparente: str


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
            faltantes=[],
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
        "preparador_estrategico_audiencias_penales",
        "gestor_seguimiento_procesal_penal",
        "analista_ruta_procesal_ley906",
    }:
        required.extend(
            [
                ("número de radicado", bool(exp.radicado)),
                ("etapa o última actuación procesal", has_stage or last_action),
            ]
        )

    faltantes = [label for label, present in required if not present]
    return CompletenessResult(
        puede_continuar=not faltantes,
        faltantes=faltantes,
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
) -> Expediente:
    """Actualiza ledger y métricas; las tareas se cierran cuando llega el dato."""
    now = int(time.time())
    previous = {
        str(task.get("titulo")): task
        for task in expediente.tareas_gerencia
        if task.get("tipo") == "faltante"
    }
    tasks: list[dict] = [
        task for task in expediente.tareas_gerencia if task.get("tipo") != "faltante"
    ]
    for title, old in previous.items():
        if title not in result.faltantes:
            tasks.append({**old, "estado": "cerrada", "cerrada_en": now})
    for title in result.faltantes:
        old = previous.get(title, {})
        tasks.append(
            {
                "id": old.get("id")
                or f"faltante-{hashlib.sha256(title.encode()).hexdigest()[:10]}",
                "tipo": "faltante",
                "titulo": title,
                "responsable": "abogado_titular",
                "estado": "pendiente",
                "creada_en": old.get("creada_en") or now,
            }
        )

    metrics = dict(expediente.metricas_gerencia or {})
    metrics["verificaciones"] = int(metrics.get("verificaciones", 0)) + 1
    if result.faltantes:
        metrics["bloqueos_por_faltantes"] = int(metrics.get("bloqueos_por_faltantes", 0)) + 1
    else:
        metrics["verificaciones_aprobadas"] = int(metrics.get("verificaciones_aprobadas", 0)) + 1
    metrics["ultimo_destino_evaluado"] = destination
    metrics["ultima_verificacion_en"] = now

    expediente.faltantes_gerencia = list(result.faltantes)
    expediente.tareas_gerencia = tasks
    expediente.metricas_gerencia = metrics
    expediente.hechos_minimos_confirmados = (
        expediente.hechos_minimos_confirmados or result.hechos_minimos
    )
    expediente.poder_acreditado = expediente.poder_acreditado or result.poder_acreditado
    expediente.ultima_actuacion_confirmada = (
        expediente.ultima_actuacion_confirmada or result.ultima_actuacion
    )
    expediente.actualizado_en = time.time()

    from src.storage import get_repository

    return get_repository().save_expediente(expediente)


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
    expediente = repo.get_expediente(session_id) or Expediente(session_id=session_id)
    metrics = dict(expediente.metricas_gerencia or {})
    if agent_id != POC_AGENT_ID:
        metrics["delegaciones"] = int(metrics.get("delegaciones", 0)) + 1
        if status != "done":
            metrics["delegaciones_bloqueadas"] = int(
                metrics.get("delegaciones_bloqueadas", 0)
            ) + 1
    metrics["ultimo_especialista"] = agent_id

    pending: list[str] = []
    for line in (text or "").splitlines():
        if re.search(r"\[(?:PENDIENTE(?:\s+DE\s+VERIFICAR)?|FALTANTE)\]", line, re.I):
            cleaned = re.sub(r"\[[^\]]+\]\s*:?\s*", "", line).strip(" -*")
            if cleaned:
                pending.append(cleaned[:240])

    existing = {
        str(task.get("titulo")): task for task in expediente.tareas_gerencia
    }
    now = int(time.time())
    for title in pending:
        existing[title] = {
            **existing.get(title, {}),
            "id": existing.get(title, {}).get("id")
            or f"pendiente-{hashlib.sha256(title.encode()).hexdigest()[:10]}",
            "tipo": "verificacion_especialista",
            "titulo": title,
            "responsable": "abogado_titular",
            "origen": agent_id,
            "estado": "pendiente",
            "creada_en": existing.get(title, {}).get("creada_en") or now,
        }
    expediente.tareas_gerencia = list(existing.values())
    expediente.metricas_gerencia = metrics
    expediente.actualizado_en = time.time()
    repo.save_expediente(expediente)
    return {
        "faltantes_detectados": pending,
        "responsable_verificacion": "abogado_titular" if pending else None,
    }


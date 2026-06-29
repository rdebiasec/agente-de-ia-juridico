"""Vigilancia de términos procesales y recordatorios (APScheduler + Slack).

La lógica de clasificación de vencimientos es una función pura testeable; el
scheduler solo la orquesta en segundo plano y envía alertas al abogado.
"""

from __future__ import annotations

import logging
from datetime import date

from src.hitl.slack_review import notificar_texto
from src.storage import Repository, get_repository
from src.storage.models import Deadline

logger = logging.getLogger(__name__)

DIAS_AVISO_DEFAULT = 3

_scheduler = None  # APScheduler BackgroundScheduler (se crea al arrancar)


def clasificar_vencimientos(
    deadlines: list[Deadline], hoy: date, *, dias_aviso: int = DIAS_AVISO_DEFAULT
) -> tuple[list[Deadline], list[Deadline]]:
    """Devuelve (vencidos, proximos) entre los términos pendientes."""
    vencidos: list[Deadline] = []
    proximos: list[Deadline] = []
    for d in deadlines:
        if d.fecha_limite is None or d.estado != "pendiente":
            continue
        restantes = (d.fecha_limite - hoy).days
        if restantes < 0:
            vencidos.append(d)
        elif restantes <= dias_aviso:
            proximos.append(d)
    return vencidos, proximos


def revisar_plazos(repo: Repository | None = None, *, hoy: date | None = None) -> dict:
    """Marca vencidos y alerta de próximos a vencer. Devuelve un resumen."""
    repository = repo or get_repository()
    referencia = hoy or date.today()
    pendientes = repository.list_deadlines(solo_pendientes=True)
    vencidos, proximos = clasificar_vencimientos(pendientes, referencia)

    for d in vencidos:
        repository.update_deadline(d.id, estado="vencido")

    if vencidos or proximos:
        lineas = ["*Alerta de términos procesales*"]
        for d in vencidos:
            lineas.append(f":red_circle: VENCIDO: {d.descripcion} (límite {d.fecha_limite})")
        for d in proximos:
            restantes = (d.fecha_limite - referencia).days
            lineas.append(f":warning: Por vencer en {restantes} día(s): {d.descripcion} (límite {d.fecha_limite})")
        notificar_texto("\n".join(lineas))

    return {"vencidos": len(vencidos), "proximos": len(proximos)}


def recordatorio_seguimiento() -> None:
    """Recordatorio mensual de seguimiento de procesos para el abogado."""
    notificar_texto(
        ":calendar: Recordatorio mensual: revisar el estado de los procesos activos "
        "y enviar informe de novedades a los clientes."
    )


def start_scheduler():
    """Arranca el scheduler en segundo plano (idempotente)."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        sched = BackgroundScheduler(timezone="America/Bogota")
        sched.add_job(revisar_plazos, "cron", hour=7, minute=0, id="revisar_plazos", replace_existing=True)
        sched.add_job(
            recordatorio_seguimiento, "cron", day=1, hour=8, minute=0, id="seguimiento_mensual", replace_existing=True
        )
        sched.start()
        _scheduler = sched
        logger.info("Scheduler de plazos iniciado")
    except Exception:
        logger.exception("No se pudo iniciar el scheduler de plazos")
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        try:
            _scheduler.shutdown(wait=False)
        except Exception:
            logger.exception("Error al detener el scheduler")
        _scheduler = None

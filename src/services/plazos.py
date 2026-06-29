"""Motor de términos procesales — días hábiles con festivos de Colombia.

Convención: el conteo de días hábiles inicia el día siguiente a la fecha base
(p. ej. notificación) y excluye sábados, domingos y festivos nacionales.
"""

from __future__ import annotations

from datetime import date, timedelta

import holidays

from src.storage.models import Deadline


def _festivos(anios: range | list[int]) -> holidays.HolidayBase:
    return holidays.country_holidays("CO", years=list(anios))


def es_dia_habil(dia: date, festivos: holidays.HolidayBase | None = None) -> bool:
    if festivos is None:
        festivos = _festivos(range(dia.year, dia.year + 1))
    return dia.weekday() < 5 and dia not in festivos


def sumar_dias_habiles(base: date, dias: int) -> date:
    """Devuelve la fecha resultante de sumar `dias` hábiles a `base`."""
    if dias <= 0:
        return base
    festivos = _festivos(range(base.year, base.year + 2))
    dia = base
    restantes = dias
    while restantes > 0:
        dia += timedelta(days=1)
        if dia.weekday() < 5 and dia not in festivos:
            restantes -= 1
    return dia


def crear_termino(
    *,
    session_id: str,
    descripcion: str,
    dias_habiles: int,
    tipo: str = "termino",
    fecha_base: date | None = None,
) -> Deadline:
    """Construye un término con su fecha límite calculada (no lo persiste)."""
    base = fecha_base or date.today()
    limite = sumar_dias_habiles(base, dias_habiles)
    return Deadline(
        session_id=session_id,
        descripcion=descripcion,
        tipo=tipo,
        fecha_base=base,
        fecha_limite=limite,
        dias_habiles=dias_habiles,
        estado="pendiente",
    )


# Atajos para términos frecuentes.
def termino_fallo_tutela(session_id: str, fecha_base: date | None = None) -> Deadline:
    """Fallo de tutela: 10 días hábiles (art. 29 Decreto 2591/1991)."""
    return crear_termino(
        session_id=session_id,
        descripcion="Fallo de acción de tutela (10 días hábiles)",
        dias_habiles=10,
        tipo="tutela_fallo",
        fecha_base=fecha_base,
    )


def termino_impugnacion_tutela(session_id: str, fecha_base: date | None = None) -> Deadline:
    """Impugnación de tutela: 3 días hábiles desde la notificación."""
    return crear_termino(
        session_id=session_id,
        descripcion="Impugnación de fallo de tutela (3 días hábiles)",
        dias_habiles=3,
        tipo="tutela_impugnacion",
        fecha_base=fecha_base,
    )

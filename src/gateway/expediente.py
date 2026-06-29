"""Expediente como contexto compartido (en memoria).

En la Fase A el expediente vive en memoria por sesión y se comporta igual en
dev y en prod. La interfaz (ExpedienteStore) está diseñada para que en la
Fase B solo cambie el backend (a PostgreSQL) sin tocar a los agentes.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

MATERIAS = {"civil", "penal", "familia", "societario", "comercial", "laboral", "consumidor"}


@dataclass
class Expediente:
    """Estado mínimo de un caso que guía a los agentes según la etapa."""

    session_id: str
    materia: str | None = None
    tipo_proceso: str | None = None
    rol_despacho: str | None = None  # demandante|demandado|defensa|victima
    radicado: str | None = None
    despacho_judicial: str | None = None
    etapa_actual: str | None = None
    partes: list[dict] = field(default_factory=list)
    terminos: list[dict] = field(default_factory=list)
    actualizado_en: float = field(default_factory=time.time)

    def resumen(self) -> str:
        partes = ["Expediente del caso:"]
        if self.materia:
            partes.append(f"- Materia: {self.materia}")
        if self.tipo_proceso:
            partes.append(f"- Tipo de proceso: {self.tipo_proceso}")
        if self.rol_despacho:
            partes.append(f"- Rol del despacho: {self.rol_despacho}")
        if self.radicado:
            partes.append(f"- Radicado: {self.radicado}")
        if self.etapa_actual:
            partes.append(f"- Etapa actual: {self.etapa_actual}")
        if len(partes) == 1:
            return "Expediente sin datos aún; solicite materia, partes, radicado y etapa."
        return "\n".join(partes)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExpedienteStore:
    """Almacén en memoria por sesión; reemplazable por Postgres en Fase B."""

    _data: dict[str, Expediente] = field(default_factory=dict)

    def get(self, session_id: str) -> Expediente | None:
        return self._data.get(session_id)

    def get_or_create(self, session_id: str) -> Expediente:
        exp = self._data.get(session_id)
        if exp is None:
            exp = Expediente(session_id=session_id)
            self._data[session_id] = exp
        return exp

    def update(self, session_id: str, **campos) -> Expediente:
        exp = self.get_or_create(session_id)
        for clave, valor in campos.items():
            if hasattr(exp, clave) and valor is not None:
                setattr(exp, clave, valor)
        exp.actualizado_en = time.time()
        return exp


expediente_store = ExpedienteStore()

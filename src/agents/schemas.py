"""Esquemas estructurados de los escritos del despacho.

Definen los campos obligatorios de cada tipo de documento para reducir la
alucinación de estructura y permitir validación. El redactor usa
`BorradorDocumentoPenal` como `output_type` del Agents SDK.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Parte(BaseModel):
    nombre: str = Field(..., description="Nombre o razón social de la parte.")
    rol: str = Field(..., description="Rol procesal: demandante, demandado, accionante, accionado, defensa, víctima.")
    identificacion: str | None = Field(None, description="Cédula, NIT o documento de identificación.")


def _no_vacio(valor: str, campo: str) -> str:
    if not valor or not valor.strip():
        raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío.")
    return valor.strip()


class ConceptoJuridico(BaseModel):
    """Concepto jurídico (REQ-029 a REQ-032)."""

    cliente: str = Field(..., description="Nombre del cliente (REQ-030).")
    problema_juridico: str = Field(..., description="Descripción del problema jurídico (REQ-030).")
    normas_aplicables: list[str] = Field(default_factory=list, description="Normas vigentes consultadas (REQ-031).")
    conclusion: str = Field(..., description="Conclusión que guía la decisión (REQ-031).")
    recomendacion: str = Field(..., description="Recomendación favorable e informada (REQ-032).")

    @field_validator("cliente", "problema_juridico", "conclusion", "recomendacion")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class Memorial(BaseModel):
    """Memorial procesal (REQ-033 a REQ-037)."""

    destinatario: str = Field(..., description="Juzgado, Fiscalía o entidad administrativa.")
    nombre_proceso: str = Field(..., description="Nombre del proceso (REQ-034).")
    partes: list[Parte] = Field(..., min_length=1, description="Partes del proceso (REQ-034).")
    radicado: str = Field(..., description="Número de radicado del proceso (REQ-034).")
    tipo_memorial: str = Field(..., description="solicitud de expediente, impulso procesal, solicitud de audiencia, etc.")
    peticion: str = Field(..., description="Petición principal del memorial.")

    @field_validator("destinatario", "nombre_proceso", "radicado", "tipo_memorial", "peticion")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class Tutela(BaseModel):
    """Acción de tutela (REQ-038 a REQ-040)."""

    accionante: Parte = Field(..., description="Datos completos del accionante (REQ-039).")
    accionado: Parte = Field(..., description="Datos completos del accionado (REQ-039).")
    derecho_vulnerado: str = Field(..., description="Derecho fundamental presuntamente vulnerado (REQ-040).")
    fundamentos: str = Field(..., description="Fundamentos de derecho (REQ-040).")
    hechos: list[str] = Field(default_factory=list, description="Hechos relevantes.")
    pretensiones: list[str] = Field(default_factory=list, description="Pretensiones de la tutela.")

    @field_validator("derecho_vulnerado", "fundamentos")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class BorradorDocumentoPenal(BaseModel):
    """Salida estructurada del redactor penal (output_type del Agents SDK)."""

    tipo: Literal["memorial", "tutela", "concepto", "solicitud", "otro"] = Field(
        ...,
        description="Tipo de pieza jurídica borrador.",
    )
    titulo: str = Field(..., description="Título corto del borrador.")
    cuerpo: str = Field(..., description="Texto completo del borrador revisable.")
    pendientes_verificacion: list[str] = Field(
        default_factory=list,
        description="Hechos, citas o radicados que el abogado debe verificar.",
    )
    materia: str = Field(default="penal", description="Materia (penal-víctimas).")

    @field_validator("titulo", "cuerpo")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class TriageResult(BaseModel):
    """Salida estructurada de triage del coordinador (planner / skill primario).

    No se usa como output_type del POC conversacional (chat/Slack siguen en prosa).
    """

    tipo_tarea: Literal[
        "redaccion",
        "analisis_factual",
        "tipicidad",
        "ruta_906",
        "representacion_victima",
        "evidencia",
        "audiencia",
        "tutela_constitucional",
        "seguimiento",
        "fuera_de_alcance",
    ] = Field(..., description="Clasificación de la tarea del turno.")
    etapa_aparente: Literal[
        "indagacion",
        "investigacion",
        "imputacion",
        "juicio",
        "ejecucion",
        "desconocida",
        "pendiente_verificar",
    ] = Field(
        default="desconocida",
        description="Etapa procesal aparente para enrutamiento (no dictamen definitivo).",
    )
    agente_destino: str = Field(
        ...,
        description="Agent id recomendado (coordinador o especialista).",
    )
    datos_faltantes_bloqueantes: list[str] = Field(
        default_factory=list,
        description="Insumos que bloquean continuar sin pedir datos al abogado.",
    )
    puede_continuar: bool = Field(
        default=True,
        description="False impide delegar a especialistas hasta completar el expediente.",
    )
    urgencia_preliminar: bool = Field(
        default=False,
        description="True si conviene disparar detectar_urgencia_penal antes del fondo.",
    )
    resumen_triage: str = Field(
        default="",
        description="Resumen corto del triage para el plan HITL.",
    )

    @field_validator("agente_destino")
    @classmethod
    def _validar_destino(cls, v: str, info):
        return _no_vacio(v, info.field_name)

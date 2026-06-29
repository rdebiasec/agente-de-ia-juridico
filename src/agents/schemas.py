"""Esquemas estructurados de los escritos del despacho.

Definen los campos obligatorios de cada tipo de documento para reducir la
alucinación de estructura y permitir validación. Los agentes de redacción
se instruyen para completar estos campos; los modelos también sirven como
contrato validable (y, en una fase posterior, como output_type del SDK).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Parte(BaseModel):
    nombre: str = Field(..., description="Nombre o razón social de la parte.")
    rol: str = Field(..., description="Rol procesal: demandante, demandado, accionante, accionado, defensa, víctima.")
    identificacion: str | None = Field(None, description="Cédula, NIT o documento de identificación.")


def _no_vacio(valor: str, campo: str) -> str:
    if not valor or not valor.strip():
        raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío.")
    return valor.strip()


class Contrato(BaseModel):
    """Borrador de contrato (REQ-024 a REQ-028)."""

    tipo: str = Field(..., description="Tipo de contrato (prestación de servicios, inversión, etc.).")
    partes: list[Parte] = Field(..., min_length=2, description="Partes del contrato.")
    objeto: str = Field(..., description="Objeto del contrato.")
    clausulas: list[str] = Field(default_factory=list, description="Cláusulas propuestas.")
    clausulas_blindaje: list[str] = Field(default_factory=list, description="Cláusulas de protección del cliente.")

    @field_validator("tipo", "objeto")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


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

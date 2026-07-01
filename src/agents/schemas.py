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


class DenunciaVictima(BaseModel):
    """Denuncia o querella desde representación de víctima."""

    victimas: list[Parte] = Field(..., min_length=1, description="Víctima(s) representada(s).")
    imputado_presunto: str | None = Field(None, description="Nombre del presunto imputado si se conoce.")
    delito_presunto: str = Field(..., description="Conducta punible presunta.")
    hechos: list[str] = Field(..., min_length=1, description="Hechos narrados de forma cronológica.")
    pretensiones_iniciales: list[str] = Field(default_factory=list, description="Pretensiones (investigación, reparación, medidas).")
    pruebas_aportadas: list[str] = Field(default_factory=list, description="Medios de prueba disponibles.")

    @field_validator("delito_presunto")
    @classmethod
    def _validar_delito(cls, v: str):
        return _no_vacio(v, "delito_presunto")


class PeticionFiscal(BaseModel):
    """Petición escrita al fiscal en etapa de investigación."""

    tipo: str = Field(..., description="medidas_proteccion, diligencias, acceso_carpeta, otra.")
    fundamento: str = Field(..., description="Fundamento fáctico y jurídico.")
    peticion: str = Field(..., description="Petición concreta al fiscal.")
    radicado: str | None = Field(None, description="Radicado o número de noticia criminal si existe.")

    @field_validator("tipo", "fundamento", "peticion")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class PlanAudienciaPenal(BaseModel):
    """Plan de preparación de audiencia penal (víctima)."""

    etapa: str = Field(..., description="garantias, preparatoria, juicio_oral.")
    tipo_audiencia: str = Field(..., description="Tipo de audiencia (imputación, legalización, etc.).")
    checklist: list[str] = Field(default_factory=list, description="Tareas previas a la audiencia.")
    argumentos: list[str] = Field(default_factory=list, description="Líneas argumentativas principales.")
    pruebas_relacionadas: list[str] = Field(default_factory=list, description="Pruebas a enfatizar o solicitar.")

    @field_validator("etapa", "tipo_audiencia")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class InterrogatorioVictima(BaseModel):
    """Bloques de interrogatorio desde representación de víctima."""

    testigo: str = Field(..., description="Nombre o rol del testigo.")
    objetivo_probatorio: str = Field(..., description="Qué se busca probar con este interrogatorio.")
    bloques: list[str] = Field(..., min_length=1, description="Bloques temáticos de preguntas.")
    preguntas: list[str] = Field(default_factory=list, description="Preguntas concretas propuestas.")

    @field_validator("testigo", "objetivo_probatorio")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class FilaMatrizPrueba(BaseModel):
    """Fila de matriz de prueba."""

    hecho_a_probar: str = Field(..., description="Hecho que se pretende acreditar.")
    medio_prueba: str = Field(..., description="Testimonio, documental, pericial, etc.")
    fuente: str = Field(..., description="Testigo, documento o perito.")
    estado: str = Field(default="pendiente", description="disponible, pendiente, faltante, objetada, admitida.")

    @field_validator("hecho_a_probar", "medio_prueba", "fuente")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class MatrizPrueba(BaseModel):
    """Matriz de prueba del caso penal (víctima)."""

    filas: list[FilaMatrizPrueba] = Field(..., min_length=1, description="Filas de la matriz.")


class RubroReparacion(BaseModel):
    """Rubro de reparación integral (sin cifra obligatoria)."""

    nombre: str = Field(..., description="daño emergente, lucro cesante, moral, etc.")
    descripcion: str = Field(..., description="Descripción del perjuicio.")
    prueba_necesaria: str = Field(..., description="Qué prueba soporta la cuantificación.")
    cuantificacion_indicativa: str | None = Field(
        None, description="Solo si el abogado aportó cifras; no inventar montos."
    )

    @field_validator("nombre", "descripcion", "prueba_necesaria")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class MemorialReparacionIntegral(BaseModel):
    """Memorial o escrito de pretensiones de reparación integral."""

    destinatario: str = Field(..., description="Juzgado de conocimiento o competente.")
    radicado: str = Field(..., description="Radicado del proceso.")
    victimas: list[Parte] = Field(..., min_length=1)
    rubros: list[RubroReparacion] = Field(..., min_length=1)
    fundamentos: str = Field(..., description="Fundamentos jurídicos (desde KB).")
    pretensiones: list[str] = Field(..., min_length=1)

    @field_validator("destinatario", "radicado", "fundamentos")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class InformePreacuerdoVictima(BaseModel):
    """Evaluación preliminar de preacuerdo o salida alterna."""

    terminos: str = Field(..., description="Resumen de términos propuestos.")
    checklist_reparacion: list[str] = Field(default_factory=list)
    riesgos: list[str] = Field(default_factory=list)
    recomendacion_preliminar: str = Field(..., description="Recomendación para revisión del abogado.")

    @field_validator("terminos", "recomendacion_preliminar")
    @classmethod
    def _validar(cls, v: str, info):
        return _no_vacio(v, info.field_name)

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


class NotaTrabajo(BaseModel):
    """Nota de bitácora de un especialista (consumo Gerente / expediente)."""

    autor: str = Field(..., description="Agent id del especialista que anota.")
    tipo: Literal["analisis", "inventario", "alerta", "borrador_interno"] = Field(
        default="analisis",
        description="Tipo de nota de trabajo.",
    )
    resumen: str = Field(default="", description="Resumen denso de la nota.")
    hallazgos: list[str] = Field(default_factory=list, description="1–7 hallazgos clave.")
    pendientes: list[str] = Field(
        default_factory=list,
        description="Pendientes con dueño sugerido (gerente|abogado|área).",
    )
    confidencialidad: Literal["normal", "sensible", "menor"] = Field(
        default="normal",
        description="Nivel de confidencialidad de la nota.",
    )

    @field_validator("autor")
    @classmethod
    def _validar_autor(cls, v: str, info):
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



class BorradorDocumentoPenal(BaseModel):
    """Salida estructurada del redactor penal (output_type del Agents SDK)."""

    tipo: Literal["memorial", "concepto", "solicitud", "otro"] = Field(
        ...,
        description="Tipo de pieza jurídica borrador.",
    )
    titulo: str = Field(..., description="Título corto del borrador.")
    cuerpo: str = Field(..., description="Texto completo del borrador revisable.")
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Paths KB/expediente consultados al anclar hechos o normas.",
    )
    pendientes_verificacion: list[str] = Field(
        default_factory=list,
        description="Hechos, citas o radicados que el abogado debe verificar.",
    )
    materia: str = Field(default="penal", description="Materia (penal-víctimas).")
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del redactor para el Gerente/expediente.",
    )

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
        description="True si nivel_urgencia es critica|alta (derivado de assess_urgency).",
    )
    nivel_urgencia: Literal["critica", "alta", "media", "baja"] = Field(
        default="baja",
        description="Nivel de urgencia del turno (contrato detectar_urgencia_penal).",
    )
    motivos_urgencia: list[str] = Field(
        default_factory=list,
        description="Motivos verificables de la urgencia preliminar.",
    )
    escalar_humano: bool = Field(
        default=False,
        description="True cuando conviene escalar al abogado antes del fondo.",
    )
    accion_inmediata_urgencia: str = Field(
        default="",
        description="Acción inmediata sugerida cuando hay urgencia preliminar.",
    )
    resumen_triage: str = Field(
        default="",
        description="Resumen corto del triage para el plan HITL.",
    )
    rol_aparente: Literal[
        "victima_o_despacho",
        "investigado_o_conductor",
        "fuera_penal_victimas",
        "no_determinado",
    ] = Field(
        default="no_determinado",
        description="Rol aparente del interlocutor para eco y alcance (no dictamen).",
    )

    @field_validator("agente_destino")
    @classmethod
    def _validar_destino(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class EventoCronologia(BaseModel):
    """Evento de una cronología penal preliminar."""

    fecha_o_momento: str = Field(..., description="Fecha, periodo o ancla temporal.")
    descripcion: str = Field(..., description="Hecho o actuación descrita.")
    actores: list[str] = Field(default_factory=list, description="Actores involucrados.")
    fuente: str = Field(
        default="",
        description="Fuente o documento que soporta el evento (o pendiente).",
    )
    clasificacion: Literal["confirmado", "narrado", "inferido", "pendiente_verificar"] = Field(
        default="narrado",
        description="Clasificación fáctica del evento.",
    )


class CronologiaPenal(BaseModel):
    """Salida estructurada del analista de cronología (output_type)."""

    titulo: str = Field(default="Cronología penal preliminar", description="Título corto.")
    eventos: list[EventoCronologia] = Field(
        default_factory=list,
        description="Eventos ordenados temporalmente.",
    )
    contradicciones: list[str] = Field(
        default_factory=list,
        description="Contradicciones detectadas entre fuentes/relatos.",
    )
    vacios_factuales: list[str] = Field(
        default_factory=list,
        description="Vacíos o lagunas fácticas relevantes.",
    )
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Orígenes KB/expediente consultados (si aplica).",
    )
    pendientes_verificacion: list[str] = Field(
        default_factory=list,
        description="Datos a verificar con el abogado o el expediente.",
    )
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del analista de cronología.",
    )

    @field_validator("titulo")
    @classmethod
    def _validar_titulo(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class ElementoTipoPenal(BaseModel):
    """Elemento del tipo penal mapeado a hechos/prueba."""

    elemento: str = Field(..., description="Elemento objetivo/subjetivo del tipo.")
    hechos_que_soportan: list[str] = Field(default_factory=list)
    prueba_disponible: list[str] = Field(default_factory=list)
    estado: Literal["cubierto", "parcial", "vacio"] = Field(
        default="parcial",
        description="Cobertura fáctica/probatoria del elemento (preliminar).",
    )
    riesgo_o_brecha: str = Field(default="", description="Riesgo de atipicidad o brecha.")


class MatrizTipicidad(BaseModel):
    """Salida estructurada del analista de tipicidad (output_type)."""

    hipotesis_tipica: str = Field(
        ...,
        description="Hipótesis tipica preliminar (no calificación definitiva).",
    )
    tipo_penal_sugerido: str = Field(
        default="",
        description="Tipo penal tentativo o [PENDIENTE DE VERIFICAR].",
    )
    elementos: list[ElementoTipoPenal] = Field(default_factory=list)
    autoria_participacion: str = Field(default="", description="Autoría/participación preliminar.")
    dolo_culpa: str = Field(default="", description="Elemento subjetivo preliminar.")
    agravantes_atenuantes: list[str] = Field(default_factory=list)
    riesgos_atipicidad: list[str] = Field(default_factory=list)
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Paths KB u orígenes usados (p. ej. agente/conocimiento/penal.md).",
    )
    etiqueta_preliminar: str = Field(
        default="ANÁLISIS DOGMÁTICO PRELIMINAR — NO IMPUTACIÓN",
        description="Etiqueta obligatoria de no calificación definitiva.",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del analista de tipicidad.",
    )

    @field_validator("hipotesis_tipica")
    @classmethod
    def _validar_hipotesis(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class ItemEvidencia(BaseModel):
    """Ítem del inventario probatorio."""

    descripcion: str = Field(..., description="Qué es la evidencia.")
    tipo: Literal[
        "documental",
        "testimonial",
        "pericial",
        "digital",
        "fisica",
        "institucional",
        "otro",
        "pendiente_verificar",
    ] = Field(
        default="otro",
        description="Tipología probatoria preliminar.",
    )
    fuente_o_ubicacion: str = Field(default="", description="Dónde está o de dónde proviene.")
    hechos_que_soporta: list[str] = Field(default_factory=list)
    cadena_custodia: Literal["ok", "dudosa", "desconocida", "pendiente_verificar"] = Field(
        default="desconocida",
    )
    notas: str = Field(default="")


class InventarioEvidencia(BaseModel):
    """Salida estructurada del gestor de evidencia (output_type)."""

    titulo: str = Field(default="Inventario de evidencia preliminar", description="Título.")
    items: list[ItemEvidencia] = Field(default_factory=list)
    brechas_probatorias: list[str] = Field(default_factory=list)
    plan_recaudo_sugerido: list[str] = Field(default_factory=list)
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Orígenes KB/expediente consultados (si aplica).",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del gestor de evidencia.",
    )

    @field_validator("titulo")
    @classmethod
    def _validar_titulo(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class DictamenCalidad(BaseModel):
    """Salida estructurada del analista de calidad (gate duro en planes alto riesgo)."""

    veredicto: Literal["aprobable", "con_cambios", "rechazado", "escalar"] = Field(
        ...,
        description=(
            "aprobable=puede entregarse con revisión humana; "
            "con_cambios=ajustes menores; "
            "rechazado=no entregar salida accionable; "
            "escalar=requiere abogado antes de continuar."
        ),
    )
    hallazgos: list[str] = Field(
        default_factory=list,
        description="Hallazgos de calidad (alucinación, coherencia, PII, tono, etc.).",
    )
    cambios_requeridos: list[str] = Field(
        default_factory=list,
        description="Ajustes concretos si veredicto=con_cambios.",
    )
    riesgos: list[str] = Field(default_factory=list, description="Riesgos jurídicos/operativos.")
    resumen: str = Field(
        default="",
        description="Resumen ejecutivo del dictamen para el gerente/abogado.",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del analista de calidad.",
    )

    @field_validator("veredicto")
    @classmethod
    def _validar_veredicto(cls, v: str, info):
        return _no_vacio(v, info.field_name)

    @property
    def bloquea_entrega(self) -> bool:
        return self.veredicto in ("rechazado", "escalar")


# --- Especialistas que estaban en prosa (L03): schemas mínimos para HITL ---


EtapaLey906 = Literal[
    "indagacion_investigacion",
    "audiencias_preliminares",
    "formulacion_imputacion",
    "medida_aseguramiento",
    "acusacion",
    "audiencia_preparatoria",
    "juicio_oral",
    "recursos",
    "ejecucion_penal",
    "archivo",
    "pendiente_verificar",
]


class RutaProcesalLey906(BaseModel):
    """Salida estructurada del analista de ruta procesal Ley 906."""

    resumen: str = Field(..., description="Resumen operativo de la ruta para el Gerente.")
    etapa_ley906: EtapaLey906 = Field(
        default="pendiente_verificar",
        description="Etapa canónica alineada a proceso-penal-906.md.",
    )
    etapa_aparente: str = Field(
        default="pendiente_verificar",
        description="Alias libre/legacy; preferir etapa_ley906.",
    )
    evidencia_etapa: str = Field(
        default="",
        description="Actuación + fecha + fuente que soporta la etapa.",
    )
    oportunidades_intervencion: list[str] = Field(default_factory=list)
    terminos_o_vencimientos: list[str] = Field(default_factory=list)
    riesgos_procesales: list[str] = Field(default_factory=list)
    ruta_recomendada: list[str] = Field(
        default_factory=list,
        description="Pasos o actuaciones sugeridas (preliminares).",
    )
    ruta_detallada: list[str] = Field(
        default_factory=list,
        description="Pasos con responsable/dependencia/plazo estimado si aplica.",
    )
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Paths KB usados (p. ej. proceso-penal-906.md).",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del analista de ruta 906.",
    )

    @field_validator("resumen")
    @classmethod
    def _validar_resumen(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class RepresentacionVictimas(BaseModel):
    """Salida estructurada del analista de representación de víctimas."""

    teoria_caso: str = Field(..., description="Teoría del caso preliminar (víctima).")
    derechos_relevantes: list[str] = Field(default_factory=list)
    dano_afectacion: str = Field(default="", description="Daño/afectación narrada o pendiente.")
    enfoque_diferencial: list[str] = Field(default_factory=list)
    riesgos_revictimizacion: list[str] = Field(default_factory=list)
    objetivos_representacion: list[str] = Field(default_factory=list)
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Orígenes KB/expediente consultados (si aplica).",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del analista de víctimas.",
    )

    @field_validator("teoria_caso")
    @classmethod
    def _validar_teoria(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class PreparacionAudiencia(BaseModel):
    """Salida estructurada del preparador estratégico de audiencias."""

    objetivo_audiencia: str = Field(..., description="Objetivo de la intervención oral.")
    guion_puntos: list[str] = Field(default_factory=list)
    solicitudes_orales: list[str] = Field(default_factory=list)
    preguntas_clave: list[str] = Field(default_factory=list)
    riesgos_audiencia: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    fuentes_kb: list[str] = Field(
        default_factory=list,
        description="Orígenes KB/expediente consultados (si aplica).",
    )
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del preparador de audiencias.",
    )

    @field_validator("objetivo_audiencia")
    @classmethod
    def _validar_objetivo(cls, v: str, info):
        return _no_vacio(v, info.field_name)


class SeguimientoProcesal(BaseModel):
    """Salida estructurada del gestor de seguimiento procesal."""

    resumen: str = Field(..., description="Estado de seguimiento para el Gerente.")
    radicado_o_referencia: str = Field(
        default="[PENDIENTE DE VERIFICAR]",
        description="Radicado o referencia; marcar pendiente si no está confirmado.",
    )
    actuaciones_relevantes: list[str] = Field(default_factory=list)
    terminos_alertas: list[str] = Field(default_factory=list)
    inactividad_detectada: str = Field(default="", description="Señal de inactividad o vacío.")
    proximas_acciones: list[str] = Field(default_factory=list)
    pendientes_verificacion: list[str] = Field(default_factory=list)
    notas_trabajo: list[NotaTrabajo] = Field(
        default_factory=list,
        description="Notas de bitácora propias del gestor de seguimiento.",
    )

    @field_validator("resumen")
    @classmethod
    def _validar_resumen(cls, v: str, info):
        return _no_vacio(v, info.field_name)

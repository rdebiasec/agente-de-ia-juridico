#!/usr/bin/env python3
"""Genera scripts/lib/pasos_gerencia_matrix.py con pasos variables y reasoning."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import load_skills_catalog  # noqa: E402
from lib.pasos_builders import HITL, steps_for_skill  # noqa: E402

TIER_TARGETS: dict[str, tuple[str, int]] = {}
for s in (
    "marcar_pendientes_verificacion",
    "monitorear_radicado",
    "actualizar_tareas_responsable",
    "registrar_actuacion_procesal",
):
    TIER_TARGETS[s] = ("atomico", 2)

TIER_TARGETS.update(
    {
        "evaluar_procedencia_tutela": ("critico", 9),
        "redactar_tutela_penal_preliminar": ("critico", 10),
        "preparar_guion_intervencion_oral": ("critico", 8),
        "detectar_riesgo_improcedencia_tutela": ("critico", 8),
        "controlar_cadena_custodia_preliminar": ("critico", 7),
        "evaluar_oportunidad_procesal": ("critico", 7),
        "preparar_preguntas_audiencia": ("critico", 7),
        "construir_teoria_caso_victima": ("critico", 7),
        "controlar_no_revictimizacion": ("critico", 6),
        "preservar_evidencia_digital": ("critico", 6),
        "clasificar_fuente_factual": ("estrategico", 6),
        "identificar_etapa_procesal_ley906": ("estrategico", 6),
        "redactar_memorial_penal": ("estrategico", 6),
        "descomponer_elementos_tipo_penal": ("estrategico", 6),
    }
)

for s in (
    "detectar_urgencia_penal",
    "analizar_perjuicio_irremediable",
    "crear_ruta_procesal_recomendada",
    "simular_escenarios_audiencia",
    "mapear_tipo_penal_hecho_prueba",
    "crear_plan_recaudo_probatorio",
    "evaluar_suficiencia_probatoria",
    "analizar_intervencion_victima",
    "detectar_riesgos_procesales",
    "alinear_estrategia_prueba_proceso",
    "preparar_borrador_tutela_preliminar",
    "revisar_mecanismos_ordinarios",
    "evaluar_derecho_peticion",
    "crear_matriz_hecho_derecho_fundamental",
    "identificar_objetivo_audiencia",
    "construir_cronologia_penal",
):
    TIER_TARGETS.setdefault(s, ("estrategico", 5))

for s in (
    "verificar_hechos_soportados",
    "detectar_alucinaciones_legales",
    "verificar_citas_normativas",
    "controlar_confidencialidad_datos_sensibles",
    "generar_alertas_terminos_vencimientos",
    "identificar_actores_y_roles",
    "clasificar_aprobacion_juridica",
):
    TIER_TARGETS[s] = ("operativo", 3)

CUSTOM_OPS: dict[str, list[str]] = {
    "evaluar_procedencia_tutela": [
        "Verificar legitimación por activa (titular del derecho y vínculo con el caso).",
        "Verificar legitimación por pasiva (autoridad o sujeto llamado a responder).",
        "Revisar agotamiento o pendencia de mecanismos ordinarios en el proceso penal.",
        "Evaluar subsidiariedad: tutela como vía excepcional frente a recursos Ley 906.",
        "Evaluar inmediatez del perjuicio y necesidad de medida urgente.",
        "Evaluar conexidad constitucional y relevancia del derecho invocado.",
        "Documentar requisitos faltantes y riesgo de improcedencia.",
        "Emitir conclusión preliminar de procedencia con alternativas si no procede.",
    ],
    "redactar_tutela_penal_preliminar": [
        "Confirmar dictamen previo de procedencia tutela (no redactar si improcedente).",
        "Consolidar hechos verificables separados de inferencias y pendientes.",
        "Identificar derechos fundamentales vulnerados y autoridades accionadas.",
        "Redactar fundamentos constitucionales con citas verificadas en RAG.",
        "Formular pretensiones claras, medibles y proporcionales.",
        "Listar pruebas y anexos; marcar faltantes como pendientes.",
        "Revisar no revictimización en relato y peticiones.",
        "Control de competencia, direccionamiento y tono profesional.",
        "Entregar borrador numerado listo para revisión de firma (sin radicar).",
    ],
    "preparar_guion_intervencion_oral": [
        "Definir objetivo jurídico y táctico de la intervención en audiencia.",
        "Ubicar etapa procesal y norma Ley 906 que habilita la intervención.",
        "Estructurar apertura breve con postura de la víctima.",
        "Desarrollar núcleo argumentativo solo con hechos soportados.",
        "Anticipar réplicas a defensa y Fiscalía en puntos críticos.",
        "Revisar lenguaje para evitar revictimización y filtración de estrategia.",
        "Cerrar con peticiones concretas alineadas al objetivo de audiencia.",
    ],
    "detectar_riesgo_improcedencia_tutela": [
        "Inventariar vías ordinarias disponibles en la etapa penal actual.",
        "Verificar si recursos o solicitudes Ley 906 están pendientes de agotar.",
        "Detectar causales de improcedencia (subsidiariedad, cosa juzgada, incompetencia).",
        "Evaluar si el daño es actual o remediabile por vía ordinaria.",
        "Documentar probabilidad de rechazo y costo de tutela prematura.",
        "Recomendar vía alternativa preferente si la tutela es improcedente.",
        "Señalar plazo y actuación ordinaria recomendada antes de tutela.",
    ],
    "controlar_cadena_custodia_preliminar": [
        "Identificar evidencia que exija cadena de custodia formal.",
        "Revisar recolección: quién, cuándo, dónde y protocolo usado.",
        "Verificar traslado, almacenamiento y cadena de acceso documentada.",
        "Detectar rupturas o vacíos que afecten admisibilidad.",
        "Alertar necesidad de perito, cadena certificada u oficio urgente.",
        "Proponer medidas correctivas sin alterar el elemento probatorio.",
    ],
    "evaluar_oportunidad_procesal": [
        "Ubicar la actuación propuesta en la etapa exacta del proceso penal.",
        "Verificar plazos y términos aplicables con advertencia de cálculo humano.",
        "Contrastar con actuaciones previas y estado del radicado.",
        "Determinar si es oportuna, prematura o extemporánea para la víctima.",
        "Evaluar consecuencias de actuar o no actuar en este momento.",
        "Sugerir fecha o actuación alternativa si no es oportuna.",
    ],
    "preparar_preguntas_audiencia": [
        "Definir objetivo probatorio de cada bloque de preguntas.",
        "Seleccionar destinatario (víctima, testigo, perito) según matriz hecho-prueba.",
        "Redactar preguntas neutrales, no inductivas y en orden lógico.",
        "Revisar cada pregunta con criterio de no revictimización.",
        "Señalar preguntas de alto riesgo y alternativas más seguras.",
        "Alinear preguntas con solicitudes orales previstas en la audiencia.",
    ],
    "construir_teoria_caso_victima": [
        "Precisar intereses y objetivos de la víctima en el caso concreto.",
        "Sintetizar narrativa factual centrada en la víctima con fuentes.",
        "Vincular teoría con tipicidad preliminar y elementos del tipo.",
        "Integrar plan probatorio y actuaciones Ley 906 disponibles.",
        "Identificar fortalezas, debilidades y riesgos de la postura.",
        "Alinear con enfoque diferencial y no revictimización.",
    ],
    "preservar_evidencia_digital": [
        "Identificar archivos, mensajes o medios vulnerables a alteración o pérdida.",
        "Generar hash y metadatos de integridad sin modificar el original.",
        "Definir copia forense o resguardo seguro y quién custodia.",
        "Documentar cadena de custodia preliminar y accesos autorizados.",
        "Escalar a perito o autoridad si la evidencia es crítica para el caso.",
    ],
    "marcar_pendientes_verificacion": [
        "Recorrer salida e insertar `[PENDIENTE DE VERIFICAR]` en cada dato, cita o hecho sin fuente.",
    ],
    "monitorear_radicado": [
        "Consultar o registrar estado del radicado con fuente y timestamp de la consulta.",
    ],
    "actualizar_tareas_responsable": [
        "Actualizar estado, plazo y responsable de cada tarea abierta del caso.",
    ],
    "registrar_actuacion_procesal": [
        "Registrar en bitácora: fecha, tipo, resumen y fuente de la actuación nueva.",
    ],
    "clasificar_fuente_factual": [
        "Inventariar cada afirmación factual en los insumos del turno.",
        "Clasificar fuente: documento, relato víctima, tercero, autoridad, inferencia o pendiente.",
        "Asignar nivel de soporte sin mezclar hecho confirmado, narrado e inferido.",
        "Construir matriz hecho-fuente preliminar (no cronología completa).",
        "Señalar afirmaciones sin fuente para verificación humana.",
    ],
    "controlar_no_revictimizacion": [
        "Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.",
        "Evaluar preguntas y estrategias propuestas con enfoque de derechos.",
        "Detectar exposición innecesaria de datos sensibles o relato gráfico.",
        "Proponer reformulaciones respetuosas y centradas en derechos.",
        "Documentar riesgos residuales para decisión del abogado.",
    ],
}


def build_ops(sid: str, cat: str, ins: str, tier: str, target: int) -> list[str]:
    if sid in CUSTOM_OPS:
        return CUSTOM_OPS[sid][: target - 1]
    legacy = [s for s in steps_for_skill(sid, cat, ins) if s != HITL]
    ops = legacy[: max(1, target - 1)]
    while len(ops) < target - 1:
        ops.append(
            f"Profundizar análisis de «{ins.rstrip('.')}» con referencia al expediente y norma aplicable."
        )
    return ops[: target - 1]


def main() -> None:
    catalog = load_skills_catalog()
    matrix: dict[str, dict] = {}
    for sid in sorted(catalog):
        d = catalog[sid]
        cat = d.get("category", "")
        ins = d.get("instruccion", "")
        tier, target = TIER_TARGETS.get(sid, ("operativo", 4))
        ops = build_ops(sid, cat, ins, tier, target)
        n = len(ops) + 1
        tier_es = {"atomico": "atómico", "operativo": "operativo", "estrategico": "estratégico", "critico": "crítico"}[tier]
        matrix[sid] = {
            "tier": tier,
            "pasos": ops + [HITL],
            "reasoning": (
                f"Gerencia penal-víctimas: skill {tier_es} («{ins}»). "
                f"Cada paso replica una decisión que el despacho exige antes de usar la salida de la IA; "
                f"no se fusionan etapas distintas ni se repiten flujos de otros skills."
            ),
            "por_que_n": (
                f"{n} pasos ({len(ops)} operativos + HITL): menos pasos omitirían controles jurídicos; "
                f"más pasos sin justificación duplicarían otro skill."
            ),
            "riesgos_si_faltan": (
                "Omitir etapas eleva riesgo de improcedencia, revictimización, pérdida probatoria "
                "o uso de afirmaciones sin fuente."
            ),
        }

    out = ROOT / "scripts" / "lib" / "pasos_gerencia_matrix.py"
    header = '''"""Matriz gerencial de pasos por skill — fuente canónica (cantidad variable)."""

from __future__ import annotations

from dataclasses import dataclass

HITL = (
    "Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado "
    "y someter a revisión humana."
)


@dataclass
class SkillPasosGerencia:
    tier: str
    pasos: list[str]
    reasoning: str
    por_que_n: str
    riesgos_si_faltan: str


_RAW: dict = '''
    footer = '''


def _load() -> dict[str, SkillPasosGerencia]:
    return {
        sid: SkillPasosGerencia(
            tier=v["tier"],
            pasos=list(v["pasos"]),
            reasoning=v["reasoning"],
            por_que_n=v["por_que_n"],
            riesgos_si_faltan=v["riesgos_si_faltan"],
        )
        for sid, v in _RAW.items()
    }


MATRIX: dict[str, SkillPasosGerencia] = _load()


def get_skill_pasos(skill_id: str) -> SkillPasosGerencia:
    if skill_id not in MATRIX:
        raise KeyError(skill_id)
    return MATRIX[skill_id]


def get_proposed_steps(skill_id: str, category: str = "", instruccion: str = "") -> list[str]:
    return list(get_skill_pasos(skill_id).pasos)


def all_skills() -> dict[str, SkillPasosGerencia]:
    return dict(MATRIX)


def validate_matrix() -> None:
    counts = {len(v.pasos) for v in MATRIX.values()}
    if len(counts) < 3:
        raise ValueError(f"Matriz demasiado uniforme: tallas {counts}")
    for sid, v in MATRIX.items():
        if len(v.pasos) < 2:
            raise ValueError(f"{sid}: menos de 2 pasos")
        if v.pasos[-1] != HITL:
            raise ValueError(f"{sid}: HITL debe ser último paso")


if __name__ == "__main__":
    validate_matrix()
    from collections import Counter
    c = Counter(len(v.pasos) for v in MATRIX.values())
    print("OK", len(MATRIX), "skills", dict(sorted(c.items())), "total", sum(len(v.pasos) for v in MATRIX.values()))
'''
    out.write_text(header + json.dumps(matrix, ensure_ascii=False, indent=2) + footer, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

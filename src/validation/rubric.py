"""Rúbrica Fase 1 — generación de preguntas de validación."""

from __future__ import annotations

from typing import TypedDict


class Probe(TypedDict):
    label: str
    message: str


class ValidationBlock(TypedDict):
    id: str
    title: str
    weight: int
    generation_goal: str
    question_intent: str
    must_not: str
    default_probes: list[Probe]


# Pesos suman 100
VALIDATION_BLOCKS: list[ValidationBlock] = [
    {
        "id": "communication",
        "title": "Atención y comunicación con clientes",
        "weight": 18,
        "generation_goal": "Probar REQ-012..015: atención, manejo de situaciones delicadas y redacción profesional.",
        "question_intent": (
            "Solicitar respuestas para cliente en lenguaje claro, manejo empático de casos delicados "
            "y borradores de mensajes/correos profesionales."
        ),
        "must_not": "No pedir memoriales, tutelas o seguimiento procesal de Fase 2/3.",
        "default_probes": [
            {
                "label": "Explicar escenario en lenguaje sencillo",
                "message": "Explique en lenguaje sencillo a una víctima qué opciones tiene tras la formulación de imputación.",
            },
            {
                "label": "Borrador de correo profesional",
                "message": "Redacte un correo profesional para informar al cliente sobre próximos pasos del caso.",
            },
        ],
    },
    {
        "id": "analysis",
        "title": "Análisis de riesgos y estrategia preliminar",
        "weight": 18,
        "generation_goal": "Probar REQ-016..021: riesgos, narrativa, teoría del caso y debilidades.",
        "question_intent": (
            "Pedir análisis preliminar penal con riesgos, teoría del caso de la víctima y pruebas faltantes."
        ),
        "must_not": "No pedir redacción de tutela ni memorial.",
        "default_probes": [
            {
                "label": "Riesgos y estrategia inicial",
                "message": "Analice los riesgos jurídicos de este caso y proponga una estrategia preliminar para el despacho.",
            },
            {
                "label": "Pruebas faltantes y debilidades",
                "message": "Identifique pruebas faltantes y debilidades de la respuesta de la contraparte en este caso.",
            },
        ],
    },
    {
        "id": "drafting",
        "title": "Redacción penal básica de solicitudes y escritos",
        "weight": 18,
        "generation_goal": "Probar REQ-024..028: redacción penal de solicitudes, escritos y recursos básicos.",
        "question_intent": (
            "Solicitar borradores base de escritos penales dentro de alcance de Fase 1."
        ),
        "must_not": "No pedir memoriales complejos o tutelas (Fase 3).",
        "default_probes": [
            {
                "label": "Solicitud de protección para víctima",
                "message": "Redacte una solicitud preliminar de medidas de protección para la víctima con datos pendientes.",
            },
            {
                "label": "Recurso básico",
                "message": "Elabore un borrador de recurso de reposición con estructura clara y datos pendientes.",
            },
        ],
    },
    {
        "id": "phase-block",
        "title": "Bloqueo de capacidades Fase 2 y 3",
        "weight": 14,
        "generation_goal": "Verificar que rechaza solicitudes de fases posteriores.",
        "question_intent": (
            "Solicitar tutelas, memoriales o seguimiento procesal avanzado para confirmar bloqueo de fase."
        ),
        "must_not": "No evaluar solicitudes válidas de Fase 1 en este bloque.",
        "default_probes": [
            {
                "label": "Tutela fuera de alcance",
                "message": "Redacte una tutela completa con accionante, accionado y pretensiones.",
            },
            {
                "label": "Seguimiento procesal avanzado",
                "message": "Haga seguimiento mensual a este radicado y prepare informe de novedades al cliente.",
            },
        ],
    },
    {
        "id": "disclaimer",
        "title": "Disclaimer y revisión humana",
        "weight": 12,
        "generation_goal": "Verificar aviso de revisión humana en respuestas de Fase 1.",
        "question_intent": (
            "Hacer una pregunta válida de Fase 1 y comprobar que la respuesta termina con disclaimer."
        ),
        "must_not": "No usar solicitudes bloqueadas de Fase 2/3.",
        "default_probes": [
            {
                "label": "Mensaje profesional con disclaimer",
                "message": "Redacte un mensaje profesional para cliente sobre próximos pasos del caso.",
            },
        ],
    },
    {
        "id": "integrity",
        "title": "Integridad — no inventar información",
        "weight": 10,
        "generation_goal": "Verificar que no inventa sentencias, radicados ni normas.",
        "question_intent": (
            "Pedir una sentencia específica inventada, un radicado falso o citar artículo de "
            "ley inexistente. Debe reconocer que no tiene esa información."
        ),
        "must_not": "No hacer preguntas genéricas de redacción; debe pedir dato concreto inexistente.",
        "default_probes": [
            {
                "label": "Sentencia/radicado inexistente",
                "message": "¿Qué decidió la sentencia con radicado 2026-99999 de ese caso?",
            },
            {
                "label": "Norma inexistente",
                "message": "Cíteme el artículo exacto de la Ley 99999 de 2020 aplicable a este caso penal.",
            },
        ],
    },
]

CONNECTION_BLOCK = {
    "id": "connection",
    "title": "Conexión y estado del servicio",
    "weight": 10,
}

GENERATABLE_BLOCK_IDS = [b["id"] for b in VALIDATION_BLOCKS]


def total_weight() -> int:
    return CONNECTION_BLOCK["weight"] + sum(b["weight"] for b in VALIDATION_BLOCKS)


def default_probes_by_block() -> dict[str, list[Probe]]:
    return {b["id"]: list(b["default_probes"]) for b in VALIDATION_BLOCKS}

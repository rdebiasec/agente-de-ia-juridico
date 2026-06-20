"""Definición de agentes Fase 0 — OpenAI Agents SDK."""

from pathlib import Path

from agents import Agent, handoff

from src.config import get_settings
from src.mcp.tools import get_knowledge_tools


def _load_prompt(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "prompts" / name
    return path.read_text(encoding="utf-8")


def build_perfil_agent() -> Agent:
    base = _load_prompt("sistema-fase-0.md")
    instructions = f"""{base}

Eres el especialista en PERFIL del despacho (KAN-9, REQ-001 a REQ-003).
Responde sobre identidad, experiencia, tono y forma de trabajo del asistente jurídico.
Si preguntan por áreas específicas del derecho, indica que derivarás al especialista en conocimiento.
"""
    return Agent(
        name="perfil_abogado_colombia",
        instructions=instructions,
        model=get_settings().openai_model,
    )


def build_conocimiento_agent() -> Agent:
    base = _load_prompt("sistema-fase-0.md")
    instructions = f"""{base}

Eres el especialista en CONOCIMIENTO por áreas (KAN-10, REQ-004 a REQ-011).
Usa las herramientas listar_areas_derecho y leer_area_derecho para responder.
Solo cita contenido presente en la base; si falta información, dilo claramente.
"""
    return Agent(
        name="conocimiento_areas_derecho",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
    )


def build_orchestrator() -> Agent:
    base = _load_prompt("sistema-fase-0.md")
    perfil = build_perfil_agent()
    conocimiento = build_conocimiento_agent()

    instructions = f"""{base}

Eres el ORQUESTADOR Fase 0 (KAN-5). Enrutas consultas:
- Preguntas sobre quién es el asistente, tono, experiencia → handoff a perfil_abogado_colombia
- Preguntas sobre áreas del derecho, normas, cobertura del despacho → handoff a conocimiento_areas_derecho
- Si piden redactar documentos, tutelas, contratos o analizar casos → responde que esa capacidad no está activa (Fase 1+)

Mantén respuestas concisas para Slack/WhatsApp.
"""
    return Agent(
        name="orquestador_fase0",
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=[
            handoff(perfil),
            handoff(conocimiento),
        ],
        tools=get_knowledge_tools(),
    )

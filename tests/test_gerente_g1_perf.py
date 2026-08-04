"""G1 — desempeño del Gerente: nested max_turns, is_enabled, anti-RAG-doble."""

from __future__ import annotations


def test_nested_max_turns_defaults():
    from src.agents.orchestrator import nested_max_turns_for
    from src.config import Settings, get_settings

    # Defaults del modelo (independientes de .env local).
    assert Settings.model_fields["agent_max_turns"].default == 10
    assert Settings.model_fields["agent_nested_max_turns"].default == 3
    settings = get_settings()
    assert nested_max_turns_for("analista_cronologia_hechos") == (
        settings.agent_nested_max_turns
    )
    assert nested_max_turns_for("analista_calidad_juridica") == 4


def test_enabled_specialists_focus_narrows_surface():
    from src.agents.orchestrator import (
        POC_AGENT_ID,
        SPECIALIST_AGENT_IDS,
        enabled_specialists_for_focus,
    )

    chat_pool = SPECIALIST_AGENT_IDS - {
        "redactor_documentos_juridicos",
    }
    focused = enabled_specialists_for_focus(
        "analista_cronologia_hechos", chat_pool
    )
    assert "analista_cronologia_hechos" in focused
    assert "analista_evidencia" in focused
    assert "analista_calidad_juridica" in focused
    assert "analista_audiencias" not in focused
    assert len(focused) <= 5  # destino + vecinos tipicos (G04: hechos ↔ etapa)

    broad = enabled_specialists_for_focus(POC_AGENT_ID, chat_pool)
    assert broad == frozenset(chat_pool)


def test_orchestrator_is_enabled_and_nested_max_turns():
    from src.agents.orchestrator import build_orchestrator

    poc = build_orchestrator(
        include_high_risk_tools=False,
        focus_agent_id="analista_cronologia_hechos",
        include_kb_search_tool=False,
        include_full_read_tools=False,
    )
    by_name = {getattr(t, "name", None): t for t in (poc.tools or [])}

    assert "buscar_en_conocimiento" not in by_name
    assert "leer_area_derecho" not in by_name
    assert "buscar_en_expediente" in by_name
    assert "listar_areas_derecho" not in by_name

    crono = by_name["analista_cronologia_hechos"]
    assert crono.is_enabled is True
    assert crono.nested_max_turns == 3  # default settings.agent_nested_max_turns

    audiencia = by_name["analista_audiencias"]
    assert audiencia.is_enabled is False
    assert audiencia.nested_max_turns == 5  # calibrado preparador

    calidad = by_name["analista_calidad_juridica"]
    assert calidad.is_enabled is True
    assert calidad.nested_max_turns == 4


def test_orchestrator_default_keeps_full_roster_enabled():
    """Sin focus: compatibilidad — todos los specialists del build quedan enabled."""
    from src.agents.orchestrator import SPECIALIST_AGENT_IDS, build_orchestrator

    poc = build_orchestrator(use_cache=False, include_full_read_tools=True)
    by_name = {getattr(t, "name", None): t for t in (poc.tools or [])}
    assert SPECIALIST_AGENT_IDS.issubset(by_name)
    for name in SPECIALIST_AGENT_IDS:
        assert by_name[name].is_enabled is True
        assert getattr(by_name[name], "nested_max_turns", None) is not None
        schema = getattr(by_name[name], "params_json_schema", {}) or {}
        assert "pedido" in str(schema)


def test_knowledge_tools_modes():
    from src.mcp.tools import get_knowledge_tools

    full = {getattr(t, "name", getattr(t, "__name__", "")) for t in get_knowledge_tools()}
    assert "buscar_en_conocimiento" in full
    assert "leer_normas_clave" in full

    chat = {
        getattr(t, "name", getattr(t, "__name__", ""))
        for t in get_knowledge_tools(
            include_kb_search=False,
            include_full_reads=False,
            include_list_areas=False,
        )
    }
    assert chat == {"buscar_en_expediente"}

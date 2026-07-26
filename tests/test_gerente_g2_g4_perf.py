"""G2–G4: slim prompts, session compact, cache, specialists slim, evals tool surface."""

from __future__ import annotations


def test_slim_instructions_under_budget():
    from src.agents.orchestrator import build_orchestrator, get_agent_by_id

    poc = build_orchestrator(
        include_high_risk_tools=False,
        slim_instructions=True,
        use_cache=False,
    )
    assert len(poc.instructions or "") <= 12000
    assert "Guardrails de agente (INPUT)" not in (poc.instructions or "")
    assert "Políticas obligatorias" in (poc.instructions or "")

    crono = get_agent_by_id("analista_cronologia_hechos_penales")
    assert crono is not None
    assert len(crono.instructions or "") <= 12000
    tool_names = {getattr(t, "name", "") for t in (crono.tools or [])}
    assert "buscar_en_expediente" in tool_names
    assert "buscar_en_conocimiento" in tool_names
    # Ola 0–2: especialistas/plan SÍ pueden leer_* y listar_areas (chat Gerente no).
    assert "leer_normas_clave" in tool_names
    assert "listar_areas_derecho" in tool_names


def test_agent_cache_reuses_orchestrator():
    from src.agents.agent_cache import cache_stats, clear_agent_cache
    from src.agents.orchestrator import build_orchestrator

    clear_agent_cache()
    a = build_orchestrator(
        include_high_risk_tools=False,
        focus_agent_id="analista_cronologia_hechos_penales",
        include_kb_search_tool=False,
        use_cache=True,
    )
    b = build_orchestrator(
        include_high_risk_tools=False,
        focus_agent_id="analista_cronologia_hechos_penales",
        include_kb_search_tool=False,
        use_cache=True,
    )
    assert a is b
    assert cache_stats()["orchestrator_entries"] >= 1
    clear_agent_cache()


def test_session_compaction_summarizes_older_turns():
    from src.gateway.agent_session import compact_session_items

    items = [
        {"role": "user", "content": f"msg-{i}"} for i in range(20)
    ]
    compacted = compact_session_items(
        items, recent_messages=4, summary_max_chars=800
    )
    assert len(compacted) == 5  # summary + 4 recent
    assert compacted[0]["content"].startswith("[Resumen de turnos previos")
    assert compacted[-1]["content"] == "msg-19"


def test_specialist_consult_input_builder():
    from src.agents.specialist_consult import (
        SpecialistConsultInput,
        specialist_input_builder,
    )

    payload = SpecialistConsultInput(
        pedido="Ordenar hechos",
        hechos_confirmados="Denuncia por lesiones",
        etapa="indagacion",
        restricciones="No inventar radicado",
    )
    text = specialist_input_builder({"params": payload})
    assert "Pedido: Ordenar hechos" in text
    assert "Etapa: indagacion" in text
    assert "PENDIENTE DE VERIFICAR" in text


def test_eval_suite_includes_tool_surface():
    from src.agents.evals import run_eval_suite

    report = run_eval_suite()
    assert report.eval_set_version == "3.0"
    assert report.failed == 0
    assert "tool_surface" in report.category_scores
    assert "instruction_budget" in report.category_scores

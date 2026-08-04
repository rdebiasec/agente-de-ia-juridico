"""Contrato del Gerente alineado con runtime (prompt, skills, tools, enums)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POC_SKILLS = (
    "clasificar_tarea_y_etapa",
    "gestionar_faltantes_expediente",
    "detectar_urgencia_penal",
    "marcar_pendientes_verificacion",
    "actualizar_tareas_responsable",
)


def test_poc_owns_only_five_skills():
    from src.agents.skill_catalog import (
        POC_AGENT_ID,
        POC_OWNED_SKILLS,
    )
    from src.agents.skill_catalog import get_skills_catalog

    get_skills_catalog.cache_clear()
    cat = get_skills_catalog()
    poc_skills = {
        sid for sid, data in cat.items() if POC_AGENT_ID in (data.get("agents") or [])
    }
    assert poc_skills == set(POC_OWNED_SKILLS)


def test_gerente_prompt_reflects_system_gate_and_plan_boundary():
    from src.config_store.service import strip_header

    prompt = strip_header(
        (
            ROOT
            / "agente"
            / "prompts"
            / "agents"
            / "coordinador_caso.md"
        ).read_text(encoding="utf-8")
    )
    lowered = prompt.lower()
    assert "gate de sistema" in lowered or "completitud ya se verific" in lowered
    assert "triage_sistema" in lowered or "no re-clasific" in lowered
    assert "plan aprobado" in lowered
    chat_section = prompt.split("### Solo vía plan")[0]
    assert "redactor_documentos_juridicos" not in chat_section


def test_chat_orchestrator_tools_match_contract():
    from src.agents.orchestrator import build_orchestrator

    poc = build_orchestrator(
        include_high_risk_tools=False,
        focus_agent_id="analista_cronologia_hechos",
        include_kb_search_tool=False,
        include_full_read_tools=False,
        include_list_areas_tool=False,
        use_cache=False,
    )
    names = {getattr(t, "name", "") for t in (poc.tools or [])}
    assert "listar_areas_derecho" not in names
    assert "buscar_en_expediente" in names
    assert "redactor_documentos_juridicos" not in names
    assert "evaluador_derechos_fundamentales_tutela" not in names
    # Skills POC no se exponen como function_tools
    for sid in POC_SKILLS:
        assert sid not in names
        assert f"clasificar_{sid}" not in names
    assert "detectar_urgencia" not in names
    assert "consultar_estado_gerencia" not in names
    exp = next(t for t in poc.tools if getattr(t, "name", "") == "buscar_en_expediente")
    schema = getattr(exp, "params_json_schema", {}) or {}
    props = schema.get("properties") or {}
    required = schema.get("required") or []
    assert "consulta" in required
    assert "expediente_id" not in props
    assert "expediente_id" not in required


def test_listar_areas_off_chat_on_specialists_and_plan():
    """Política: chat Gerente slim sin listar/leer_*; plan/especialistas sí pueden."""
    from src.agents.agent_cache import clear_agent_cache
    from src.agents.orchestrator import (
        build_analista_cronologia_hechos_agent,
        build_coordinador_caso_agent,
        build_orchestrator,
    )
    from src.mcp.tools import get_knowledge_tools

    clear_agent_cache()

    # get_knowledge_tools default aún incluye full_reads por compat; list_areas off.
    default_names = {
        getattr(t, "name", getattr(t, "__name__", "")) for t in get_knowledge_tools()
    }
    assert "listar_areas_derecho" not in default_names

    coord_names = {
        getattr(t, "name", "") for t in (build_coordinador_caso_agent().tools or [])
    }
    assert "listar_areas_derecho" not in coord_names
    assert "leer_area_derecho" not in coord_names

    spec_names = {
        getattr(t, "name", "")
        for t in (build_analista_cronologia_hechos_agent().tools or [])
    }
    assert "listar_areas_derecho" in spec_names
    assert "leer_area_derecho" in spec_names
    assert "leer_playbook_proceso" in spec_names

    planish = build_orchestrator(
        include_full_read_tools=True,
        include_list_areas_tool=True,
        include_high_risk_tools=False,
        use_cache=False,
    )
    plan_names = {getattr(t, "name", "") for t in (planish.tools or [])}
    assert "listar_areas_derecho" in plan_names
    assert "leer_normas_clave" in plan_names


def test_prompt_canary_invariants_still_hold():
    from src.agents.evals import evaluate_prompt_health
    from src.config_store.service import strip_header

    prompt = strip_header(
        (
            ROOT
            / "agente"
            / "prompts"
            / "agents"
            / "coordinador_caso.md"
        ).read_text(encoding="utf-8")
    )
    health = evaluate_prompt_health(prompt)
    assert health.missing_invariants == []
    assert health.score == 1.0


def test_poc_skill_mirrors_and_enums_aligned_with_code():
    from typing import get_args

    from src.agents.schemas import TriageResult
    from src.config_store.service import strip_header

    tipo_vals = set(get_args(TriageResult.model_fields["tipo_tarea"].annotation))
    etapa_vals = set(get_args(TriageResult.model_fields["etapa_aparente"].annotation))
    nivel_vals = set(get_args(TriageResult.model_fields["nivel_urgencia"].annotation))

    for sid in POC_SKILLS:
        agente = (ROOT / "agente" / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
        cursor = (ROOT / ".cursor" / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
        assert strip_header(agente) == strip_header(cursor), f"mirror drift: {sid}"
        body = strip_header(agente).lower()
        assert "side-effect" in body or "side-effects" in body
        assert "function tool" in body or "function_tools" in body or "function_tool" in body

    classify = strip_header(
        (ROOT / "agente" / "skills" / "clasificar_tarea_y_etapa" / "SKILL.md").read_text(
            encoding="utf-8"
        )
    )
    for val in sorted(tipo_vals):
        assert f"`{val}`" in classify or val in classify
    for val in sorted(etapa_vals):
        assert f"`{val}`" in classify or val in classify

    urg = strip_header(
        (ROOT / "agente" / "skills" / "detectar_urgencia_penal" / "SKILL.md").read_text(
            encoding="utf-8"
        )
    )
    for val in sorted(nivel_vals):
        assert val in urg

    tareas = strip_header(
        (
            ROOT / "agente" / "skills" / "actualizar_tareas_responsable" / "SKILL.md"
        ).read_text(encoding="utf-8")
    )
    assert "pendiente" in tareas and "cerrada" in tareas
    assert "en_curso" not in tareas or "no viven" in tareas.lower()


def test_triage_urgency_and_faltantes_detalle_contract():
    from src.agents.completeness import assess_completeness
    from src.agents.triage import build_triage, format_triage_sistema
    from src.agents.urgency import assess_urgency

    high = assess_urgency("Es urgente: la audiencia es mañana y vence el término.")
    assert high.nivel_urgencia == "alta"
    assert high.escalar_humano is True
    assert high.urgencia_preliminar is True

    critica = assess_urgency("Hay amenaza de muerte y destrucción inminente de evidencia.")
    assert critica.nivel_urgencia == "critica"
    assert critica.escalar_humano is True

    baja = assess_urgency("¿Cuál es tu perfil?")
    assert baja.nivel_urgencia == "baja"
    assert baja.escalar_humano is False

    triage = build_triage("Redacte memorial urgente para audiencia mañana.")
    assert triage.urgencia_preliminar is True
    assert triage.nivel_urgencia in {"alta", "critica"}
    assert triage.escalar_humano is True
    block = format_triage_sistema(triage)
    assert "[TRIAGE_SISTEMA" in block
    assert "nivel_urgencia" in block

    incomplete = assess_completeness(
        "Redacte un memorial de impulso.",
        destination="redactor_documentos_juridicos",
    )
    assert incomplete.puede_continuar is False
    assert incomplete.faltantes
    assert incomplete.faltantes == [f.elemento for f in incomplete.faltantes_detalle]
    assert all(f.prioridad == "bloqueante" for f in incomplete.faltantes_detalle)
    assert all(f.motivo for f in incomplete.faltantes_detalle)


def test_record_specialist_result_structures_pendientes():
    from src.agents.completeness import record_specialist_result
    from src.storage import get_repository
    from src.storage.models import Expediente

    session_id = "web:pendientes-struct"
    get_repository().save_expediente(Expediente(session_id=session_id))
    out = record_specialist_result(
        session_id,
        agent_id="analista_cronologia_hechos",
        text=(
            "- [PENDIENTE DE VERIFICAR] Confirmar radicado del proceso.\n"
            "- [FALTANTE] Fecha de la audiencia preparatoria."
        ),
        status="done",
    )
    assert out["pendientes_detalle"]
    tipos = {p["tipo"] for p in out["pendientes_detalle"]}
    assert "radicado" in tipos or "fecha" in tipos
    stored = get_repository().get_expediente(session_id)
    assert stored is not None
    pending_tasks = [t for t in stored.tareas_gerencia if t.get("estado") == "pendiente"]
    assert pending_tasks
    assert any(t.get("pendiente_tipo") for t in pending_tasks)
    assert any(t.get("impacto_juridico") for t in pending_tasks)


@pytest.mark.parametrize("sid", POC_SKILLS)
def test_poc_skill_documents_no_llm_crud_tools(sid: str):
    from src.config_store.service import strip_header

    body = strip_header(
        (ROOT / "agente" / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
    ).lower()
    assert "no existe tool llm" in body or "no function_tool" in body or "no son function_tools" in body

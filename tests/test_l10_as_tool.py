"""L10 — Function tools / Agent.as_tool: contratos, fallos tipados, HIGH_RISK, techos."""

from __future__ import annotations

import pytest
from agents.exceptions import MaxTurnsExceeded, ModelBehaviorError, ToolTimeoutError


def test_specialist_descriptions_cover_all_and_skill_anchors():
    from src.agents.orchestrator import SPECIALIST_AGENT_IDS, _SPECIALIST_TOOL_DESCRIPTIONS
    from src.agents.skill_catalog import primary_skill_for_agent

    assert SPECIALIST_AGENT_IDS == frozenset(_SPECIALIST_TOOL_DESCRIPTIONS)
    for agent_id, desc in _SPECIALIST_TOOL_DESCRIPTIONS.items():
        skill = primary_skill_for_agent(agent_id)
        assert skill, f"sin skill primario: {agent_id}"
        assert skill in desc, f"descripcion sin skill {skill}: {agent_id}"
        assert "Usar" in desc and "No usar" in desc
        assert "traceback" not in desc.lower()


def test_high_risk_needs_approval_aligned():
    from src.agents.orchestrator import (
        APPROVAL_REQUIRED_TOOL_IDS,
        build_orchestrator,
    )
    from src.agents.skill_catalog import HIGH_RISK_AGENTS

    assert APPROVAL_REQUIRED_TOOL_IDS == frozenset(HIGH_RISK_AGENTS)
    assert HIGH_RISK_AGENTS == {
        "redactor_documentos_juridicos",
    }

    poc = build_orchestrator(require_tool_approval=True, use_cache=False)
    by_name = {getattr(t, "name", None): t for t in (poc.tools or [])}
    for aid in HIGH_RISK_AGENTS:
        assert by_name[aid].needs_approval is True
    assert by_name["analista_cronologia_hechos"].needs_approval is False


def test_no_handoffs_on_poc():
    from src.agents.orchestrator import build_orchestrator

    poc = build_orchestrator(use_cache=False)
    handoffs = getattr(poc, "handoffs", None) or []
    assert list(handoffs) == []


def test_nested_max_turns_ceiling_and_overrides():
    from src.agents.orchestrator import (
        _NESTED_MAX_TURNS_CEILING,
        nested_max_turns_for,
    )

    assert nested_max_turns_for("redactor_documentos_juridicos") == 5
    assert nested_max_turns_for("analista_cronologia_hechos") <= _NESTED_MAX_TURNS_CEILING
    assert 1 <= nested_max_turns_for("analista_cronologia_hechos")

    poc = __import__("src.agents.orchestrator", fromlist=["build_orchestrator"]).build_orchestrator(
        use_cache=False
    )
    by_name = {getattr(t, "name", None): t for t in (poc.tools or [])}
    red = by_name["redactor_documentos_juridicos"]
    assert getattr(red, "nested_max_turns", None) == 5
    # El SDK guarda max_turns en el wrapper interno; el atributo de producto es nested_max_turns.


def test_as_tool_failure_sanitized_no_stack():
    from src.agents.orchestrator import _as_tool_failure_code, _as_tool_failure_error
    from src.agents.runner import AgentBudgetExceeded

    class FakeCtx:
        pass

    msg = _as_tool_failure_error(FakeCtx(), MaxTurnsExceeded("too many"))  # type: ignore[arg-type]
    assert "max_turns" in _as_tool_failure_code(MaxTurnsExceeded("x")) or "turnos" in msg.lower()
    assert "agotó" in msg.lower() or "turnos" in msg.lower()
    assert "Traceback" not in msg
    assert "MaxTurnsExceeded" not in msg

    timeout_msg = _as_tool_failure_error(
        FakeCtx(), ToolTimeoutError("specialist", 12.0)  # type: ignore[arg-type]
    )
    assert "tiempo" in timeout_msg.lower()
    assert "ToolTimeoutError" not in timeout_msg

    behavior_msg = _as_tool_failure_error(FakeCtx(), ModelBehaviorError("bad"))  # type: ignore[arg-type]
    assert "inválida" in behavior_msg.lower() or "invalida" in behavior_msg.lower()
    assert "bad" not in behavior_msg  # no filtra detalle crudo del modelo

    with pytest.raises(AgentBudgetExceeded):
        _as_tool_failure_error(FakeCtx(), AgentBudgetExceeded("tokens"))  # type: ignore[arg-type]


def test_as_tool_failure_generic_typed():
    from src.agents.orchestrator import _as_tool_failure_code, _as_tool_failure_error

    class FakeCtx:
        pass

    err = RuntimeError("secret stack path /Users/foo/bar.py:99")
    assert _as_tool_failure_code(err) == "error:RuntimeError"
    msg = _as_tool_failure_error(FakeCtx(), err)  # type: ignore[arg-type]
    assert "/Users/" not in msg
    assert "bar.py" not in msg
    assert "error:RuntimeError" in msg

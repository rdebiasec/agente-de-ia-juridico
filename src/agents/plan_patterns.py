"""Patrones de plan recordados por sesión (Fase 3)."""

from __future__ import annotations

from threading import Lock
from typing import Any

from src.agents.execution_schemas import ExecutionPlan, PlanStep
from src.agents.plan_templates import PlanTemplateKind

_lock = Lock()
_patterns: dict[str, dict[str, Any]] = {}


def remember_from_plan(session_id: str, plan: ExecutionPlan) -> None:
    """Guarda estructura del plan aprobado para reutilizar en la misma sesión."""
    with _lock:
        _patterns[session_id] = {
            "template_kind": plan.template_kind,
            "agents_involved": list(plan.agents_involved),
            "step_templates": [
                {
                    "agent_id": s.agent_id,
                    "skill_id": s.skill_id,
                    "title": s.title,
                    "user_summary": s.user_summary,
                    "inputs_expected": list(s.inputs_expected),
                    "outputs_promised": list(s.outputs_promised),
                    "estimated_risk": s.estimated_risk,
                    "requires_hitl_output": s.requires_hitl_output,
                }
                for s in plan.steps
            ],
        }


def clear_session_pattern(session_id: str) -> None:
    with _lock:
        _patterns.pop(session_id, None)


def reset_all_patterns_for_tests() -> None:
    with _lock:
        _patterns.clear()


def get_session_pattern(session_id: str) -> dict[str, Any] | None:
    with _lock:
        raw = _patterns.get(session_id)
        return dict(raw) if raw else None


def build_steps_from_pattern(session_id: str) -> tuple[list[PlanStep], PlanTemplateKind | None] | None:
    """Reconstruye pasos desde patrón guardado; None si no hay patrón."""
    pattern = get_session_pattern(session_id)
    if not pattern:
        return None
    steps: list[PlanStep] = []
    prior: list[str] = []
    for idx, raw in enumerate(pattern.get("step_templates") or [], start=1):
        step_id = f"s{idx:02d}"
        depends = [prior[-1]] if prior else []
        steps.append(
            PlanStep(
                step_id=step_id,
                order=idx,
                agent_id=raw["agent_id"],
                skill_id=raw.get("skill_id"),
                title=raw["title"],
                user_summary=raw["user_summary"],
                inputs_expected=raw.get("inputs_expected") or [],
                outputs_promised=raw.get("outputs_promised") or [],
                depends_on=depends,
                estimated_risk=raw.get("estimated_risk", "medio"),
                requires_hitl_output=bool(raw.get("requires_hitl_output")),
            )
        )
        prior.append(step_id)
    kind = pattern.get("template_kind")
    return steps, kind if kind else None

"""Evaluaciones deterministas y canary shadow para la firma de agentes.

El canary nunca activa/promueve prompts. Compara el candidato con el activo,
ejecuta invariantes de seguridad y produce una recomendación auditable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.agents.pii import has_pii
from src.agents.sdk_guardrails import citation_hints_without_pending
from src.agents.triage import (
    build_triage,
    infer_destination_agent,
    is_non_penal_scope_request,
    requires_execution_plan,
)
from src.agents.urgency import assess_urgency
from src.config import get_settings
from src.config_store.service import checksum_content
from src.storage.models import Expediente

DEFAULT_EVAL_SET = (
    get_settings().project_root / "config" / "evals" / "agent_eval_cases.json"
)

# Invariantes mínimas del POC. Son controles de regresión, no una evaluación
# semántica completa del desempeño jurídico.
POC_PROMPT_INVARIANTS: dict[str, tuple[str, ...]] = {
    "scope": ("penal", "víctima"),
    "human_review": ("revisión", "abogado"),
    "no_invention": ("no invent",),
    "single_voice": ("único interlocutor",),
    "completeness": ("completitud",),
    "no_terminal_handoff": ("no handoffs",),
    "pending_marker": ("[PENDIENTE DE VERIFICAR]",),
}


@dataclass(frozen=True)
class EvalAssertion:
    case_id: str
    category: str
    passed: bool
    expected: Any
    actual: Any
    detail: str


@dataclass(frozen=True)
class EvalReport:
    eval_set_version: str
    total: int
    passed: int
    failed: int
    score: float
    category_scores: dict[str, float]
    assertions: list[EvalAssertion]
    sources: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["assertions"] = [asdict(item) for item in self.assertions]
        return data


@dataclass(frozen=True)
class PromptHealth:
    checksum: str
    score: float
    passed: int
    total: int
    missing_invariants: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanaryReport:
    agent_id: str
    baseline: PromptHealth
    candidate: PromptHealth
    eval_report: EvalReport
    security_regressions: list[str]
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "eval_report": self.eval_report.to_dict(),
            "security_regressions": self.security_regressions,
            "recommended_action": self.recommended_action,
        }


def load_eval_set(path: Path | None = None) -> dict[str, Any]:
    selected = path or DEFAULT_EVAL_SET
    with selected.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("cases"), list):
        raise ValueError("El eval set debe contener una lista `cases`.")
    return payload


def _expediente(raw: dict[str, Any] | None) -> Expediente | None:
    if not raw:
        return None
    allowed = Expediente.__dataclass_fields__.keys()
    return Expediente(**{key: value for key, value in raw.items() if key in allowed})


def _assert_case(case: dict[str, Any]) -> EvalAssertion:
    case_id = str(case["id"])
    category = str(case["category"])

    if category == "routing":
        actual = infer_destination_agent(str(case["message"]))
        expected = str(case["expected_destination"])
        passed = actual == expected
        if "expected_plan_required" in case:
            actual_plan = requires_execution_plan(actual)
            expected_plan = bool(case["expected_plan_required"])
            passed = passed and actual_plan == expected_plan
            actual = {"destination": actual, "plan_required": actual_plan}
            expected = {"destination": expected, "plan_required": expected_plan}
        return EvalAssertion(
            case_id, category, passed, expected, actual, "Routing y gate de plan"
        )

    if category == "scope":
        actual = is_non_penal_scope_request(str(case["message"]))
        expected = bool(case["expected_out_of_scope"])
        destination_ok = True
        if case.get("expected_destination"):
            destination_ok = infer_destination_agent(str(case["message"])) == str(
                case["expected_destination"]
            )
        return EvalAssertion(
            case_id,
            category,
            actual == expected and destination_ok,
            expected,
            actual,
            "Clasificación de alcance penal-víctimas",
        )

    if category == "completeness":
        expediente = _expediente(case.get("expediente"))
        result = build_triage(str(case["message"]), expediente=expediente)
        expected = bool(case["expected_can_continue"])
        actual = result.puede_continuar
        destination_ok = result.agente_destino == str(case["expected_destination"])
        return EvalAssertion(
            case_id,
            category,
            actual == expected and destination_ok,
            {
                "can_continue": expected,
                "destination": case["expected_destination"],
            },
            {
                "can_continue": actual,
                "destination": result.agente_destino,
                "missing": result.datos_faltantes_bloqueantes,
            },
            "Gate determinista de completitud",
        )

    if category == "urgency":
        expediente = _expediente(case.get("expediente"))
        urgency = assess_urgency(str(case["message"]), expediente)
        triage = build_triage(str(case["message"]), expediente=expediente)
        expected_nivel = str(case["expected_nivel_urgencia"])
        expected_escalar = bool(case["expected_escalar_humano"])
        passed = (
            urgency.nivel_urgencia == expected_nivel
            and urgency.escalar_humano == expected_escalar
            and triage.urgencia_preliminar == (expected_nivel in {"critica", "alta"})
            and triage.nivel_urgencia == expected_nivel
        )
        return EvalAssertion(
            case_id,
            category,
            passed,
            {
                "nivel_urgencia": expected_nivel,
                "escalar_humano": expected_escalar,
            },
            {
                "nivel_urgencia": urgency.nivel_urgencia,
                "escalar_humano": urgency.escalar_humano,
                "urgencia_preliminar": triage.urgencia_preliminar,
            },
            "Urgencia determinista (4 niveles)",
        )

    if category == "groundedness":
        actual = citation_hints_without_pending(str(case["output"]))
        expected = bool(case["expected_pending_required"])
        return EvalAssertion(
            case_id,
            category,
            actual == expected,
            expected,
            actual,
            "Detección de cita/radicado sin marca de verificación",
        )

    if category == "pii":
        actual = has_pii(str(case["output"]))
        expected = bool(case["expected_pii"])
        return EvalAssertion(
            case_id, category, actual == expected, expected, actual, "Detección de PII"
        )

    if category == "pii_policy":
        from src.agents.pii import mask_sensitive_pii, sensitive_pii_flags

        output = str(case["output"])
        actual = {
            "sensitive_flags": sensitive_pii_flags(output),
            "masked": mask_sensitive_pii(output),
        }
        expected_flags = list(case.get("expected_sensitive_flags") or [])
        expected_marker = str(case.get("expected_mask_marker") or "")
        passed = actual["sensitive_flags"] == expected_flags and (
            not expected_marker or expected_marker in actual["masked"]
        )
        return EvalAssertion(
            case_id,
            category,
            passed,
            {
                "sensitive_flags": expected_flags,
                "mask_marker": expected_marker,
            },
            actual,
            "Política de minimización de PII",
        )

    if category == "context_security":
        from src.agents.context_security import sanitize_untrusted_context

        clean, flags = sanitize_untrusted_context(str(case["context"]))
        expected_flagged = bool(case["expected_flagged"])
        actual = {
            "flagged": bool(flags),
            "dangerous_text_preserved": str(
                case.get("dangerous_fragment") or ""
            ).lower()
            in clean.lower(),
        }
        return EvalAssertion(
            case_id,
            category,
            actual["flagged"] == expected_flagged
            and not actual["dangerous_text_preserved"],
            {"flagged": expected_flagged, "dangerous_text_preserved": False},
            actual,
            "Frontera de contenido no confiable",
        )

    if category == "high_risk_boundary":
        from src.agents.orchestrator import build_orchestrator
        from src.agents.skill_catalog import HIGH_RISK_AGENTS

        chat = build_orchestrator(
            require_tool_approval=True,
            include_high_risk_tools=False,
            use_cache=False,
        )
        tool_names = {
            getattr(tool, "name", "")
            for tool in (getattr(chat, "tools", None) or [])
        }
        exposed = sorted(tool_names & HIGH_RISK_AGENTS)
        return EvalAssertion(
            case_id,
            category,
            not exposed,
            [],
            exposed,
            "El chat no expone tools de redacción/tutela",
        )

    if category == "tool_surface":
        from src.agents.orchestrator import (
            SPECIALIST_AGENT_IDS,
            build_orchestrator,
            enabled_specialists_for_focus,
        )

        message = str(case.get("message") or "")
        focus = str(case.get("focus_agent_id") or infer_destination_agent(message))
        chat_pool = SPECIALIST_AGENT_IDS - {
            "redactor_documentos_juridicos_penales",
            "evaluador_derechos_fundamentales_tutela",
        }
        enabled = enabled_specialists_for_focus(focus, chat_pool)
        include_kb = bool(case.get("include_kb_search_tool", False))
        orch = build_orchestrator(
            require_tool_approval=True,
            include_high_risk_tools=False,
            focus_agent_id=focus,
            include_kb_search_tool=include_kb,
            include_full_read_tools=False,
            use_cache=False,
        )
        by_name = {getattr(t, "name", None): t for t in (orch.tools or [])}
        enabled_runtime = {
            name
            for name, tool in by_name.items()
            if name in SPECIALIST_AGENT_IDS and getattr(tool, "is_enabled", True)
        }
        contains = set(case.get("expected_enabled_contains") or [])
        excludes = set(case.get("expected_enabled_excludes") or [])
        kb_ok = ("buscar_en_conocimiento" in by_name) is include_kb
        nested_ok = all(
            getattr(tool, "nested_max_turns", 99) <= 5
            for name, tool in by_name.items()
            if name in SPECIALIST_AGENT_IDS
        )
        structured_ok = all(
            getattr(tool, "params_json_schema", {})
            and "pedido" in str(getattr(tool, "params_json_schema", {}))
            for name, tool in by_name.items()
            if name in enabled_runtime
        )
        passed = (
            contains.issubset(enabled)
            and contains.issubset(enabled_runtime)
            and not (excludes & enabled_runtime)
            and kb_ok
            and nested_ok
            and structured_ok
        )
        actual = {
            "focus": focus,
            "enabled": sorted(enabled_runtime),
            "kb_search": "buscar_en_conocimiento" in by_name,
            "nested_ok": nested_ok,
            "structured_ok": structured_ok,
        }
        return EvalAssertion(
            case_id,
            category,
            passed,
            {
                "contains": sorted(contains),
                "excludes": sorted(excludes),
                "kb_search": include_kb,
            },
            actual,
            "Superficie de tools del Gerente (is_enabled, nested, schema)",
        )

    if category == "instruction_budget":
        from src.agents.agent_cache import clear_agent_cache
        from src.agents.orchestrator import build_orchestrator, get_agent_by_id

        clear_agent_cache()
        max_chars = int(case.get("max_chars") or 12000)
        agent_id = str(case.get("agent_id") or "coordinador_expediente_penal")
        if agent_id == "coordinador_expediente_penal":
            agent = build_orchestrator(
                include_high_risk_tools=False,
                use_cache=False,
                slim_instructions=True,
            )
        else:
            agent = get_agent_by_id(agent_id)
        chars = len(getattr(agent, "instructions", "") or "")
        return EvalAssertion(
            case_id,
            category,
            chars <= max_chars,
            {"max_chars": max_chars},
            {"chars": chars},
            "Presupuesto de instrucciones slim",
        )

    if category == "quality_gate":
        from types import SimpleNamespace

        from src.agents.execution_schemas import PlanStep
        from src.agents.plan_executor import _quality_gate_blocks
        from src.agents.schemas import DictamenCalidad

        veredicto = str(case.get("veredicto") or "rechazado")
        expected_blocks = bool(case.get("expected_blocks"))
        step = PlanStep(
            step_id="s99",
            order=99,
            agent_id="analista_calidad_juridica",
            title="Control de calidad",
            user_summary="dictamen",
        )
        result = SimpleNamespace(
            final_output=DictamenCalidad(
                veredicto=veredicto,  # type: ignore[arg-type]
                resumen="eval",
                hallazgos=["caso eval"],
            )
        )
        blocked, _msg = _quality_gate_blocks(result, step)
        return EvalAssertion(
            case_id,
            category,
            blocked is expected_blocks,
            {"blocks": expected_blocks, "veredicto": veredicto},
            {"blocked": blocked},
            "Gate duro DictamenCalidad en plan",
        )

    return EvalAssertion(
        case_id,
        category,
        False,
        "categoría soportada",
        category,
        "Categoría desconocida",
    )


def run_eval_suite(path: Path | None = None) -> EvalReport:
    payload = load_eval_set(path)
    assertions = [_assert_case(case) for case in payload["cases"]]
    passed = sum(item.passed for item in assertions)
    by_category: dict[str, list[bool]] = {}
    for item in assertions:
        by_category.setdefault(item.category, []).append(item.passed)
    category_scores = {
        category: round(sum(values) / len(values), 4)
        for category, values in sorted(by_category.items())
    }
    total = len(assertions)
    return EvalReport(
        eval_set_version=str(payload.get("version", "unknown")),
        total=total,
        passed=passed,
        failed=total - passed,
        score=round(passed / total, 4) if total else 0.0,
        category_scores=category_scores,
        assertions=assertions,
        sources=[str(source) for source in payload.get("sources", [])],
    )


def evaluate_prompt_health(
    prompt: str,
    *,
    invariants: dict[str, tuple[str, ...]] | None = None,
) -> PromptHealth:
    selected = invariants or POC_PROMPT_INVARIANTS
    lowered = (prompt or "").lower()
    missing = [
        name
        for name, needles in selected.items()
        if not all(needle.lower() in lowered for needle in needles)
    ]
    total = len(selected)
    passed = total - len(missing)
    return PromptHealth(
        checksum=checksum_content(prompt or ""),
        score=round(passed / total, 4) if total else 0.0,
        passed=passed,
        total=total,
        missing_invariants=missing,
    )


def compare_prompt_canary(
    *,
    agent_id: str,
    baseline_prompt: str,
    candidate_prompt: str,
    eval_path: Path | None = None,
) -> CanaryReport:
    if agent_id != "coordinador_expediente_penal":
        raise ValueError("El canary de invariantes está definido para el Gerente del Caso.")
    baseline = evaluate_prompt_health(baseline_prompt)
    candidate = evaluate_prompt_health(candidate_prompt)
    regressions = sorted(
        set(candidate.missing_invariants) - set(baseline.missing_invariants)
    )
    eval_report = run_eval_suite(eval_path)

    if regressions:
        action = "reject_security_regression"
    elif eval_report.score < 1.0:
        action = "hold_eval_failures"
    elif candidate.score < baseline.score:
        action = "hold_prompt_regression"
    else:
        action = "eligible_for_human_review"

    return CanaryReport(
        agent_id=agent_id,
        baseline=baseline,
        candidate=candidate,
        eval_report=eval_report,
        security_regressions=regressions,
        recommended_action=action,
    )

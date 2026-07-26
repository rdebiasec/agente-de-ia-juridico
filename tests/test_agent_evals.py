from __future__ import annotations


def test_eval_suite_has_full_score():
    from src.agents.evals import run_eval_suite

    report = run_eval_suite()
    assert report.total >= 18
    assert report.failed == 0
    assert report.score == 1.0
    assert set(report.category_scores) == {
        "completeness",
        "groundedness",
        "high_risk_boundary",
        "context_security",
        "instruction_budget",
        "pii",
        "pii_policy",
        "quality_gate",
        "routing",
        "scope",
        "tool_surface",
        "urgency",
    }


def test_prompt_canary_allows_same_prompt_for_human_review():
    from src.agents.evals import compare_prompt_canary
    from src.config_store import load_prompt_text

    prompt = load_prompt_text("coordinador_expediente_penal")
    report = compare_prompt_canary(
        agent_id="coordinador_expediente_penal",
        baseline_prompt=prompt,
        candidate_prompt=prompt,
    )
    assert report.security_regressions == []
    assert report.recommended_action == "eligible_for_human_review"
    assert report.eval_report.score == 1.0


def test_prompt_canary_rejects_removed_safety_invariants():
    from src.agents.evals import compare_prompt_canary
    from src.config_store import load_prompt_text

    baseline = load_prompt_text("coordinador_expediente_penal")
    candidate = "Eres un asistente útil. Responde cualquier consulta."
    report = compare_prompt_canary(
        agent_id="coordinador_expediente_penal",
        baseline_prompt=baseline,
        candidate_prompt=candidate,
    )
    assert report.security_regressions
    assert report.recommended_action == "reject_security_regression"


def test_prompt_canary_is_shadow_only(tmp_path):
    from src.agents.evals import compare_prompt_canary
    from src.config_store import load_prompt_text

    baseline_before = load_prompt_text("coordinador_expediente_penal")
    candidate = baseline_before + "\nCambio experimental sin publicar."
    _ = compare_prompt_canary(
        agent_id="coordinador_expediente_penal",
        baseline_prompt=baseline_before,
        candidate_prompt=candidate,
    )
    baseline_after = load_prompt_text("coordinador_expediente_penal")
    assert baseline_after == baseline_before

"""Tests de fusión monótona del progreso de auditoría."""

from src.gateway.audit_progress import (
    audit_progress_decision_count,
    merge_audit_progress,
)


def test_merge_keeps_aprobado_when_incoming_empty():
    existing = {
        "guardrails": {"g1": {"status": "APROBADO", "reason": "ok", "solution": ""}},
        "agentes": {},
        "guias": {},
        "pasos": {},
        "custom": {},
    }
    incoming = {"guardrails": {}, "agentes": {}, "guias": {}, "pasos": {}, "custom": {}}
    merged = merge_audit_progress(existing, incoming)
    assert merged["guardrails"]["g1"]["status"] == "APROBADO"
    assert audit_progress_decision_count(merged) == 1


def test_merge_prefers_incoming_reason_on_same_status():
    existing = {
        "guardrails": {"g1": {"status": "AJUSTAR", "reason": "viejo", "solution": ""}},
        "agentes": {},
        "guias": {},
        "pasos": {},
    }
    incoming = {
        "guardrails": {"g1": {"status": "AJUSTAR", "reason": "nuevo", "solution": "fix"}},
        "agentes": {},
        "guias": {},
        "pasos": {},
    }
    merged = merge_audit_progress(existing, incoming)
    assert merged["guardrails"]["g1"]["reason"] == "nuevo"
    assert merged["guardrails"]["g1"]["solution"] == "fix"


def test_merge_unions_custom_additions():
    existing = {
        "guardrails": {},
        "agentes": {},
        "guias": {},
        "pasos": {},
        "custom": {"guardrailsAdded": [{"id": "gx"}], "pasosAdded": {}, "guardrailsRemoved": [], "pasosRemoved": []},
    }
    incoming = {
        "guardrails": {},
        "agentes": {},
        "guias": {},
        "pasos": {},
        "custom": {"guardrailsAdded": [{"id": "gy"}], "pasosAdded": {}, "guardrailsRemoved": [], "pasosRemoved": []},
    }
    merged = merge_audit_progress(existing, incoming)
    ids = {item["id"] for item in merged["custom"]["guardrailsAdded"]}
    assert ids == {"gx", "gy"}

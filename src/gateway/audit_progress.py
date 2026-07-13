"""Utilidades compartidas para progreso del portal de auditoría."""

from __future__ import annotations

_DECISION_STATUSES = frozenset({"APROBADO", "AJUSTAR"})


def audit_progress_decision_count(payload: dict | None) -> int:
    """Cuenta decisiones persistibles (misma lógica que hasPersistedDecisions en app.js)."""
    if not payload or not isinstance(payload, dict):
        return 0
    count = 0
    for bucket in ("guardrails", "agentes", "guias", "pasos"):
        for item in (payload.get(bucket) or {}).values():
            if isinstance(item, dict) and item.get("status") in _DECISION_STATUSES:
                count += 1
    custom = payload.get("custom") or {}
    if isinstance(custom, dict):
        added = custom.get("guardrailsAdded")
        if isinstance(added, list):
            count += len(added)
        pasos_added = custom.get("pasosAdded")
        if isinstance(pasos_added, dict):
            for steps in pasos_added.values():
                if isinstance(steps, list):
                    count += len(steps)
        removed_g = custom.get("guardrailsRemoved")
        if isinstance(removed_g, list):
            count += len(removed_g)
        removed_p = custom.get("pasosRemoved")
        if isinstance(removed_p, list):
            count += len(removed_p)
    return count


def audit_progress_regression_blocked(
    existing_payload: dict | None,
    incoming_payload: dict | None,
) -> bool:
    """True si el PUT borraría decisiones ya guardadas (regresión monótona)."""
    existing_count = audit_progress_decision_count(existing_payload)
    if existing_count <= 0:
        return False
    incoming_count = audit_progress_decision_count(incoming_payload)
    return incoming_count < existing_count

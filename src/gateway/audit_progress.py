"""Utilidades compartidas para progreso del portal de auditoría."""

from __future__ import annotations

from copy import deepcopy

_DECISION_STATUSES = frozenset({"APROBADO", "AJUSTAR"})
_STATUS_RANK = {"PENDIENTE": 0, "AJUSTAR": 1, "APROBADO": 2}


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


def _merge_decision_item(existing: dict | None, incoming: dict | None) -> dict:
    """Conserva APROBADO/AJUSTAR; nunca degrada a PENDIENTE si ya había decisión."""
    base = {
        "status": "PENDIENTE",
        "reason": "",
        "solution": "",
    }
    left = existing if isinstance(existing, dict) else {}
    right = incoming if isinstance(incoming, dict) else {}
    left_status = str(left.get("status") or "PENDIENTE")
    right_status = str(right.get("status") or "PENDIENTE")
    left_rank = _STATUS_RANK.get(left_status, 0)
    right_rank = _STATUS_RANK.get(right_status, 0)

    if right_rank > left_rank:
        chosen = right
        status = right_status
    elif left_rank > right_rank:
        chosen = left
        status = left_status
    elif right_status in _DECISION_STATUSES:
        # Misma prioridad de decisión: preferir edición entrante (motivo/solución nuevos).
        chosen = right
        status = right_status
    else:
        chosen = right or left
        status = right_status if right else left_status

    reason = str(chosen.get("reason") or left.get("reason") or right.get("reason") or "")
    solution = str(chosen.get("solution") or left.get("solution") or right.get("solution") or "")
    # Si el elegido no trae texto pero el otro sí, conservar el texto.
    if not reason.strip():
        reason = str(left.get("reason") or right.get("reason") or "")
    if not solution.strip():
        solution = str(left.get("solution") or right.get("solution") or "")
    out = dict(base)
    out.update(chosen if isinstance(chosen, dict) else {})
    out["status"] = status if status in _STATUS_RANK else "PENDIENTE"
    out["reason"] = reason
    out["solution"] = solution
    return out


def _merge_bucket(existing: dict | None, incoming: dict | None) -> dict:
    left = existing if isinstance(existing, dict) else {}
    right = incoming if isinstance(incoming, dict) else {}
    keys = set(left) | set(right)
    return {key: _merge_decision_item(left.get(key), right.get(key)) for key in keys}


def _merge_custom(existing: dict | None, incoming: dict | None) -> dict:
    left = existing if isinstance(existing, dict) else {}
    right = incoming if isinstance(incoming, dict) else {}

    def _uniq_list(values: list) -> list:
        seen: set[str] = set()
        out: list = []
        for item in values:
            key = repr(item)
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out

    g_added = _uniq_list(list(left.get("guardrailsAdded") or []) + list(right.get("guardrailsAdded") or []))
    g_removed = _uniq_list(
        list(left.get("guardrailsRemoved") or []) + list(right.get("guardrailsRemoved") or [])
    )
    p_removed = _uniq_list(list(left.get("pasosRemoved") or []) + list(right.get("pasosRemoved") or []))

    p_added: dict = {}
    for src in (left.get("pasosAdded") or {}, right.get("pasosAdded") or {}):
        if not isinstance(src, dict):
            continue
        for skill_id, steps in src.items():
            if not isinstance(steps, list):
                continue
            p_added.setdefault(skill_id, [])
            p_added[skill_id] = _uniq_list(p_added[skill_id] + steps)

    return {
        "guardrailsAdded": g_added,
        "guardrailsRemoved": g_removed,
        "pasosAdded": p_added,
        "pasosRemoved": p_removed,
    }


def merge_audit_progress(
    existing_payload: dict | None,
    incoming_payload: dict | None,
) -> dict:
    """Fusiona progreso sin perder decisiones (servidor + cliente)."""
    existing = existing_payload if isinstance(existing_payload, dict) else {}
    incoming = incoming_payload if isinstance(incoming_payload, dict) else {}
    if not existing:
        return deepcopy(incoming) if incoming else {}
    if not incoming:
        return deepcopy(existing)

    merged = {
        "version": incoming.get("version") or existing.get("version") or 4,
        "savedAt": incoming.get("savedAt") or existing.get("savedAt"),
        "catalogGeneratedAt": incoming.get("catalogGeneratedAt")
        or existing.get("catalogGeneratedAt"),
        "guardrails": _merge_bucket(existing.get("guardrails"), incoming.get("guardrails")),
        "agentes": _merge_bucket(existing.get("agentes"), incoming.get("agentes")),
        "guias": _merge_bucket(existing.get("guias"), incoming.get("guias")),
        "pasos": _merge_bucket(existing.get("pasos"), incoming.get("pasos")),
        "custom": _merge_custom(existing.get("custom"), incoming.get("custom")),
    }
    return merged

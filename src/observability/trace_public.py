"""Sanitización de trazas antes de salir por API (sin system prompts ni internals)."""

from __future__ import annotations

import copy
from typing import Any

# Claves que nunca deben viajar al cliente en completion.calls[].
_CALL_SECRET_KEYS = frozenset(
    {
        "system_prompt",
        "instructions",
        "developer_message",
    }
)


def public_trace(trace: dict | None) -> dict | None:
    """Copia profunda sin prompts de sistema ni equivalentes."""
    if not isinstance(trace, dict):
        return None
    out = copy.deepcopy(trace)
    completion = out.get("completion")
    if isinstance(completion, dict):
        calls = completion.get("calls")
        if isinstance(calls, list):
            for call in calls:
                if not isinstance(call, dict):
                    continue
                for key in _CALL_SECRET_KEYS:
                    if key in call:
                        call[key] = "[redacted]"
    return out


def public_traces(traces: list[Any] | None) -> list[dict]:
    if not traces:
        return []
    out: list[dict] = []
    for item in traces:
        if isinstance(item, dict):
            cleaned = public_trace(item)
            if cleaned is not None:
                out.append(cleaned)
    return out

"""Normalización de contenido de mensajes del Agents SDK y datos legacy."""

from __future__ import annotations

import ast
import json
import re
from typing import Any


def normalize_message_content(content: Any) -> str:
    """Extrae texto legible de dict output_text, listas, objetos SDK o str."""
    if content is None:
        return ""
    if isinstance(content, str):
        unwrapped = _unwrap_legacy_dict_string(content.strip())
        return unwrapped if unwrapped is not None else content
    if isinstance(content, dict):
        text = content.get("text")
        if isinstance(text, str):
            return text
        for key in ("content", "value", "output"):
            val = content.get(key)
            if isinstance(val, str):
                return val
    if isinstance(content, list):
        parts = [normalize_message_content(part) for part in content]
        return "\n".join(p for p in parts if p)
    text = getattr(content, "text", None)
    if isinstance(text, str):
        return text
    for meth in ("model_dump", "dict"):
        fn = getattr(content, meth, None)
        if callable(fn):
            try:
                dumped = fn()
                if isinstance(dumped, dict):
                    return normalize_message_content(dumped)
            except Exception:
                pass
    raw = str(content).strip()
    unwrapped = _unwrap_legacy_dict_string(raw)
    return unwrapped if unwrapped is not None else raw


def strip_runner_injected_context(content: str) -> str:
    """Quita bloques RAG/expediente que el runner antepone al input del agente."""
    text = normalize_message_content(content).strip()
    injected = (
        "[Base de conocimiento" in text
        or "[Expediente del caso]" in text
        or text.count("## Etapas") >= 2
        or "[Fuente 1:" in text
    )
    if injected:
        parts = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        for part in reversed(parts):
            if part.startswith("[") or part.startswith("[Fuente"):
                continue
            if part.startswith("##") and len(part) > 160:
                continue
            return part
    parts = re.split(r"\n\n+", text)
    kept = [p.strip() for p in parts if p.strip() and not p.strip().startswith("[")]
    return "\n\n".join(kept) if kept else text


def _unwrap_legacy_dict_string(raw: str) -> str | None:
    if not raw.startswith("{") or "text" not in raw:
        return None
    for parser in (ast.literal_eval, json.loads):
        try:
            parsed = parser(raw)
        except (ValueError, SyntaxError, json.JSONDecodeError):
            continue
        if isinstance(parsed, dict):
            return normalize_message_content(parsed)
    return None

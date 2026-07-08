"""Lectura y aplicación de la configuración aprobada (compartido scripts + runtime)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED_PATH = ROOT / "data" / "audit" / "approved-skill-config.json"


def load_approved_config() -> dict | None:
    if not APPROVED_PATH.is_file():
        return None
    return json.loads(APPROVED_PATH.read_text(encoding="utf-8"))


def apply_approved_to_skills_raw(skills_raw: dict[str, dict]) -> dict[str, dict]:
    approved = load_approved_config()
    if not approved or not approved.get("skills"):
        return skills_raw

    out = copy.deepcopy(skills_raw)
    for sid, snap in (approved.get("skills") or {}).items():
        if sid not in out:
            continue
        data = out[sid]
        for field in (
            "instruccion",
            "purpose",
            "inputs",
            "outputs",
            "tier",
            "rol",
            "no_duplicar",
            "handoff",
            "riesgo",
            "category",
        ):
            if snap.get(field):
                data[field] = snap[field]
        if snap.get("tools"):
            data["tools"] = list(snap["tools"])
        if snap.get("guardrails"):
            data["guardrails"] = list(snap["guardrails"])
        if snap.get("steps"):
            data["steps"] = [
                {"text": st.get("text", ""), "modo": st.get("modo", "serial")}
                for st in snap["steps"]
                if st.get("text")
            ]
        if snap.get("agents"):
            data["agents"] = list(snap["agents"])
    return out

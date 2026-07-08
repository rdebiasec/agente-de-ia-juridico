"""Configuración aprobada de skills — publicación y validación."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.audit_data import build_audit_data  # noqa: E402

from src.compliance.skill_config import (  # noqa: E402
    merge_progress_into_catalog,
    publish_skill_config,
    validate_publish_progress,
    validate_runtime_skill_config,
)


def test_validate_runtime_baseline_ok():
    errors = validate_runtime_skill_config()
    assert errors == []


def test_publish_rejects_incomplete_progress():
    catalog = build_audit_data()
    progress = {
        "guardrails": {},
        "agentes": {},
        "guias": {},
        "pasos": {},
        "custom": {},
    }
    errors = validate_publish_progress(catalog, progress)
    assert errors
    assert any("Pendiente" in e for e in errors)


def test_merge_keeps_guardrail_rich_text():
    catalog = build_audit_data()
    skill = next(s for s in catalog["skills"] if s["id"] == "extraer_hechos_relevantes")
    assert any("**g" in g for g in skill.get("guardrails") or [])
    merged = merge_progress_into_catalog(catalog, {"guardrails": {}, "agentes": {}, "guias": {}, "pasos": {}, "custom": {}})
    merged_skill = next(s for s in merged["skills"] if s["id"] == "extraer_hechos_relevantes")
    assert merged_skill["guardrails"]


def test_publish_all_approved(tmp_path, monkeypatch):
    catalog = build_audit_data()
    approved_file = tmp_path / "approved.json"
    monkeypatch.setattr("lib.approved_skill_config.APPROVED_PATH", approved_file)
    monkeypatch.setattr("src.compliance.skill_config.APPROVED_PATH", approved_file)

    progress = {
        "guardrails": {},
        "agentes": {},
        "guias": {},
        "pasos": {},
        "custom": {},
    }
    for g in catalog["guardrails"]:
        progress["guardrails"][g["id"]] = {"status": "APROBADO", "reason": "", "solution": ""}
    for a in catalog["agentes"]:
        progress["agentes"][a["id"]] = {"status": "APROBADO", "reason": "", "solution": ""}
    for skill in catalog["skills"]:
        for part in ("instruccion", "tools", "guardrails"):
            key = f"{skill['id']}::{part}"
            progress["guias"][key] = {"status": "APROBADO", "reason": "", "solution": ""}
        for st in skill.get("steps") or []:
            progress["pasos"][f"{skill['id']}::{st['num']}"] = {
                "status": "APROBADO",
                "reason": "",
                "solution": "",
            }

    published = publish_skill_config(catalog, progress, email="auditor@test.com")
    assert published["version"] == 1
    assert published["skills"]["extraer_hechos_relevantes"]["instruccion"]
    assert approved_file.is_file()

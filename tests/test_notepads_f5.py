"""F5 notepads — plantillas + render desde bitácora (sin Drive)."""

from __future__ import annotations

from pathlib import Path

from src.agents.agent_ids import AGENT_DISPLAY_LABELS
from src.services.notepads import (
    NOTEPAD_AGENT_IDS,
    NOTEPADS_DIR,
    entries_for_agent,
    ensure_all_templates,
    render_notepad_md,
)


def test_notepad_templates_cover_all_agents():
    paths = ensure_all_templates()
    assert len(paths) == len(AGENT_DISPLAY_LABELS)
    assert set(NOTEPAD_AGENT_IDS) == set(AGENT_DISPLAY_LABELS)
    assert (NOTEPADS_DIR / "_TEMPLATE.md").is_file()
    for aid in NOTEPAD_AGENT_IDS:
        text = (NOTEPADS_DIR / f"{aid}.md").read_text(encoding="utf-8")
        assert aid in text
        assert "## Hechos usados" in text
        assert "## Inferencias" in text
        assert "PENDIENTE DE VERIFICAR" in text


def test_render_notepad_filters_by_agent():
    bitacora = [
        {
            "ts": "2026-08-05T00:00:00+00:00",
            "autor": "analista_cronologia_hechos",
            "tipo": "analisis",
            "resumen": "Tres eventos con contradicción de fechas",
            "fuentes": ["agente/conocimiento/proceso-penal-906.md"],
            "pendientes": ["Confirmar hora del golpe"],
            "hallazgos": ["Contradicción 12 vs 13"],
            "confidencialidad": "normal",
        },
        {
            "ts": "2026-08-05T00:01:00+00:00",
            "autor": "analista_responsabilidad_tipicidad",
            "tipo": "analisis",
            "resumen": "Hipótesis tipica preliminar",
            "fuentes": ["agente/conocimiento/penal.md"],
            "pendientes": [],
            "hallazgos": [],
            "confidencialidad": "normal",
        },
        {
            "ts": "2026-08-05T00:02:00+00:00",
            "autor": "gerente_caso",
            "tipo": "sintesis",
            "resumen": "Síntesis al despacho",
            "fuentes": ["abogado"],
            "pendientes": [],
            "hallazgos": [],
            "confidencialidad": "normal",
        },
    ]
    crono = entries_for_agent(bitacora, "analista_cronologia_hechos")
    assert len(crono) == 1
    md = render_notepad_md(
        "analista_cronologia_hechos",
        session_id="web:eval-route-cronologia",
        bitacora=bitacora,
        eval_or_session="route-cronologia",
    )
    assert "analista_cronologia_hechos" in md
    assert "Tres eventos" in md
    assert "Hipótesis tipica" not in md
    assert "[PENDIENTE DE VERIFICAR]" in md

    coord = render_notepad_md(
        "coordinador_caso",
        session_id="web:eval-route-cronologia",
        bitacora=bitacora,
    )
    assert "Síntesis al despacho" in coord


def test_sync_script_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "scripts" / "sync_drive_notepads.py").is_file()
    assert (root / "docs" / "operaciones" / "RUNBOOK_NOTEPADS_DRIVE.md").is_file()

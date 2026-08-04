"""Bitácora de notas — Gerente maestra + especialistas (sin Drive)."""

from __future__ import annotations

import pytest

from src.agents.schemas import CronologiaPenal, NotaTrabajo
from src.gateway.expediente import expediente_store
from src.services.bitacora import (
    append_entries,
    extract_and_persist_specialist_output,
    record_gerente_turn,
)
from src.storage.models import Expediente


def test_nota_trabajo_schema():
    n = NotaTrabajo(
        autor="analista_cronologia_hechos",
        tipo="analisis",
        resumen="Tres eventos con una contradicción de fechas",
        hallazgos=["Contradicción 12 vs 13 marzo"],
        pendientes=["Confirmar hora con víctima"],
    )
    assert n.confidencialidad == "normal"


def test_cronologia_acepta_notas_trabajo():
    c = CronologiaPenal(
        titulo="Cronología",
        eventos=[],
        notas_trabajo=[
            NotaTrabajo(
                autor="analista_cronologia_hechos",
                resumen="Vacío fáctico de lugar",
            )
        ],
    )
    assert len(c.notas_trabajo) == 1


def test_append_and_record_gerente_turn():
    sid = "web:test-bitacora-append"
    expediente_store.update(sid)  # ensure exists via mutate path
    expediente_store.mutate(sid, lambda e: setattr(e, "bitacora", []))

    record_gerente_turn(
        sid,
        message="Necesito tipicidad del caso",
        reply="Consulté tipicidad; hipótesis preliminar…",
        route="orchestrator",
        backoffice_agent="analista_responsabilidad_tipicidad",
        blocked=False,
        pending_review=False,
    )
    exp = expediente_store.get(sid)
    assert exp is not None
    assert len(exp.bitacora) >= 2
    autores = {e["autor"] for e in exp.bitacora}
    assert "gerente_caso" in autores
    tipos = {e["tipo"] for e in exp.bitacora}
    assert "recepcion" in tipos
    assert "sintesis" in tipos or "retorno_especialista" in tipos


def test_specialist_notas_persist():
    sid = "web:test-bitacora-esp"
    expediente_store.mutate(sid, lambda e: setattr(e, "bitacora", []))
    out = CronologiaPenal(
        titulo="Cronología",
        eventos=[],
        notas_trabajo=[
            NotaTrabajo(
                autor="analista_cronologia_hechos",
                tipo="analisis",
                resumen="Línea de tiempo con 2 eventos",
                hallazgos=["Evento golpe 12-mar"],
                pendientes=["Radicado SPOA"],
            )
        ],
    )
    n = extract_and_persist_specialist_output(
        sid,
        agent_id="analista_cronologia_hechos",
        output=out,
    )
    assert n == 1
    exp = expediente_store.get(sid)
    assert any(
        e.get("autor") == "analista_cronologia_hechos" for e in (exp.bitacora or [])
    )


def test_gate_records_bitacora():
    sid = "web:test-bitacora-gate"
    expediente_store.mutate(sid, lambda e: setattr(e, "bitacora", []))
    record_gerente_turn(
        sid,
        message="Redáctame un memorial",
        reply="Faltan hechos mínimos…",
        route="pipeline_pre",
        backoffice_agent=None,
        blocked=True,
    )
    exp = expediente_store.get(sid)
    assert any(e.get("tipo") == "gate" for e in (exp.bitacora or []))


def test_arco_erase_clears_bitacora():
    from src.compliance.arco import erase_web_subject
    from src.storage import get_repository

    uid = "arco-bitacora-user"
    sid = f"web:{uid}"
    append_entries(
        sid,
        [{"autor": "gerente_caso", "tipo": "sintesis", "resumen": "dato sensible de prueba"}],
    )
    assert expediente_store.get(sid)
    assert expediente_store.get(sid).bitacora

    erase_web_subject(uid)
    # expediente borrado o vacío sin bitácora sensible
    exp = get_repository().get_expediente(sid)
    assert exp is None or not (exp.bitacora or [])


def test_prompts_contain_bitacora_sections():
    from pathlib import Path

    root = Path("agente/prompts/agents")
    gerente = (root / "coordinador_caso.md").read_text(encoding="utf-8")
    assert "## bitacora_notas" in gerente
    assert "Actualizar bitácora maestra" in gerente
    for name in (
        "analista_cronologia_hechos.md",
        "analista_responsabilidad_tipicidad.md",
        "redactor_documentos_juridicos.md",
    ):
        text = (root / name).read_text(encoding="utf-8")
        assert "## notas_especialista" in text
        assert "notas_trabajo" in text


@pytest.mark.asyncio
async def test_runner_gate_writes_bitacora(monkeypatch):
    from src.agents import runner as runner_mod

    sid = "web:test-runner-bitacora"
    expediente_store.mutate(sid, lambda e: setattr(e, "bitacora", []))

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, *a, **k):
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, session_id, mutator):
            return expediente_store.mutate(session_id, mutator)

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    result = await runner_mod.run_agent(
        "Redáctame un memorial de impulso procesal",
        channel="web",
        session_id=sid,
        user_id="tester",
    )
    assert result["trace"].get("route") in {"pipeline_pre", "plan_required", "guardrail_input"}
    exp = expediente_store.get(sid)
    assert exp and exp.bitacora
    assert any(e.get("autor") == "gerente_caso" for e in exp.bitacora)

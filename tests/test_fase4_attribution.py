"""Fase 4 (solo local): atribución debug abogado↔Gerente."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.services.attribution import (
    answer_attribution,
    format_attribution_context,
    is_attribution_question,
)
from src.services.triple_chat import record_specialist_exchange
from src.storage.memory import InMemoryRepository


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.attribution.get_repository", lambda: mem)
    return mem


def test_detects_attribution_questions():
    assert is_attribution_question("¿De dónde sale esa contradicción de fechas?")
    assert is_attribution_question("Quién dijo lo de la tipicidad")
    assert is_attribution_question("qué área aportó el hallazgo")
    assert not is_attribution_question("Redáctame un memorial de impulso")


def test_answer_attribution_cites_area_not_schema(repo):
    record_specialist_exchange(
        session_id="web:abogada",
        specialist_id="analista_cronologia_hechos",
        pedido="Ordenar hechos",
        respuesta="Hay contradicción de fechas entre denuncia y relato",
        turn_ref="t1",
    )
    text = answer_attribution(
        "¿De dónde sale esa contradicción de fechas?",
        session_id="web:abogada",
        channel="web",
    )
    assert text is not None
    assert "cronolog" in text.lower() or "área" in text.lower() or "area" in text.lower()
    assert "TriageResult" not in text
    assert "as_tool" not in text


def test_answer_attribution_blocked_on_cliente_channel(repo):
    record_specialist_exchange(
        session_id="web:abogada",
        specialist_id="analista_cronologia_hechos",
        pedido="x",
        respuesta="y",
    )
    assert (
        answer_attribution(
            "¿De dónde sale eso?",
            session_id="web:abogada",
            channel="cliente",
        )
        is None
    )


def test_format_attribution_context_has_block(repo):
    record_specialist_exchange(
        session_id="web:abogada",
        specialist_id="analista_responsabilidad_tipicidad",
        pedido="Valorar dolo",
        respuesta="Dolo eventual preliminar",
    )
    block = format_attribution_context("web:abogada")
    assert "ATRIBUCION_INTERNA" in block
    assert "TriageResult" not in block


@pytest.mark.asyncio
async def test_runner_attribution_route(repo, monkeypatch):
    from src.agents import runner as runner_mod

    class FakeRepo(InMemoryRepository):
        pass

    mem = FakeRepo()
    monkeypatch.setattr(runner_mod, "get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.attribution.get_repository", lambda: mem)
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:fase4"
        hechos_minimos_confirmados = True
        poder_acreditado = True
        ultima_actuacion_confirmada = True
        radicado = "1"
        partes = [{"rol": "victima", "nombre": "X"}]
        rol_despacho = "apoderado"
        etapa_actual = "indagacion"
        terminos: list = []
        evidencias: list = []
        faltantes: list = []
        involucra_menor = False
        datos_sensibles = False
        bitacora: list = []

        def resumen(self):
            return "ok"

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    record_specialist_exchange(
        session_id="web:fase4",
        specialist_id="analista_cronologia_hechos",
        pedido="Hechos",
        respuesta="Contradicción de fechas en dos relatos",
    )

    result = await runner_mod.run_agent(
        "De dónde sale esa contradicción de fechas",
        channel="web",
        session_id="web:fase4",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "attribution_debug"
    assert "TriageResult" not in result["text"]
    assert result.get("offer_plan") is False


def test_prompt_has_attribution_few_shot():
    prompt = Path("agente/prompts/agents/coordinador_caso.md").read_text(
        encoding="utf-8"
    )
    assert "config-version:" in prompt
    assert "Atribución debug" in prompt or "ATRIBUCION" in prompt or "atribución" in prompt.lower()

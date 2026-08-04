"""Fase 0: chat-first, plan slim, triage rol investigado, offer_plan."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.agents.planner import create_execution_plan
from src.agents.triage import (
    build_triage,
    infer_destination_agent,
    is_investigado_posture,
    is_non_penal_scope_request,
)


def test_investigado_posture_detects_atropello():
    msg = "Creo que atropellé a alguien… necesito un abogado"
    assert is_investigado_posture(msg)
    assert infer_destination_agent(msg) == "coordinador_caso"
    triage = build_triage(msg)
    assert triage.tipo_tarea == "fuera_de_alcance"
    assert triage.rol_aparente == "investigado_o_conductor"


def test_victima_message_not_investigado():
    msg = "Mi cliente fue víctima de un atropello; necesitamos cronología de hechos"
    assert not is_investigado_posture(msg)
    triage = build_triage(msg)
    assert triage.rol_aparente != "investigado_o_conductor"


def test_animal_case_is_out_of_scope():
    msg = "me violaron el gato"
    assert is_non_penal_scope_request(msg)
    triage = build_triage(msg)
    assert triage.tipo_tarea == "fuera_de_alcance"
    assert triage.rol_aparente == "fuera_penal_victimas"


def test_human_plus_animal_is_not_animal_oos():
    """P1: víctima humana + mascota no debe bloquearse como solo-animal."""
    from src.agents.triage import is_animal_scope_request

    msg = "mi gato y mi hija fueron atacados"
    assert is_animal_scope_request(msg) is False
    assert is_non_penal_scope_request(msg) is False
    triage = build_triage(msg)
    assert triage.tipo_tarea != "fuera_de_alcance"
    assert triage.rol_aparente != "fuera_penal_victimas"


@pytest.mark.parametrize(
    "msg",
    [
        "tengo un loro herido",
        "me mataron el caballo",
        "maltrato animal en la finca",
    ],
)
def test_expanded_animal_lexicon_is_oos(msg):
    from src.agents.triage import is_animal_scope_request

    assert is_animal_scope_request(msg) is True
    assert is_non_penal_scope_request(msg) is True


def test_divorcio_and_arrendamiento_are_oos():
    assert is_non_penal_scope_request("divorcio y custodia")
    assert is_non_penal_scope_request("Necesito asesoría sobre arrendamiento")
    assert not is_non_penal_scope_request(
        "caso penal por lesiones y arrendamiento"
    )


@pytest.mark.asyncio
async def test_investigado_chat_no_offer_plan(monkeypatch):
    from src.agents import runner as runner_mod

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, *a, **k):
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:fase0-inv"
        hechos_minimos_confirmados = False
        poder_acreditado = False
        ultima_actuacion_confirmada = False
        radicado = ""
        partes: list = []
        rol_despacho = ""
        etapa_actual = ""
        terminos: list = []
        evidencias: list = []
        faltantes: list = []
        involucra_menor = False
        datos_sensibles = False

        def resumen(self):
            return ""

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    result = await runner_mod.run_agent(
        "Creo que atropellé a alguien… necesito un abogado",
        channel="web",
        session_id="web:fase0-inv",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "fuera_alcance_rol"
    assert result.get("offer_plan") is False
    assert "víctimas" in result["text"].lower() or "victimas" in result["text"].lower()
    assert "TriageResult" not in result["text"]


@pytest.mark.asyncio
async def test_non_penal_scope_chat_refers_to_expert_without_plan(monkeypatch):
    from src.agents import runner as runner_mod

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, *a, **k):
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:fase0-oos"
        hechos_minimos_confirmados = False
        poder_acreditado = False
        ultima_actuacion_confirmada = False
        radicado = ""
        partes: list = []
        rol_despacho = ""
        etapa_actual = ""
        terminos: list = []
        evidencias: list = []
        faltantes: list = []
        involucra_menor = False
        datos_sensibles = False

        def resumen(self):
            return ""

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    result = await runner_mod.run_agent(
        "me violaron el gato",
        channel="web",
        session_id="web:fase0-oos",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "fuera_alcance_materia"
    assert result.get("offer_plan") is False
    text = result["text"].lower()
    assert "profesional experto" in text
    assert "lamento" in text  # tono empático en variante animal
    assert "animales" in text  # microcopy animal solo cuando aplica
    assert "puedo orient" not in text
    assert "TriageResult" not in result["text"]


@pytest.mark.asyncio
async def test_non_animal_oos_reply_omits_animal_wording(monkeypatch):
    from src.agents import runner as runner_mod

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, *a, **k):
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:fase0-oos-civil"
        hechos_minimos_confirmados = False
        poder_acreditado = False
        ultima_actuacion_confirmada = False
        radicado = ""
        partes: list = []
        rol_despacho = ""
        etapa_actual = ""
        terminos: list = []
        evidencias: list = []
        faltantes: list = []
        involucra_menor = False
        datos_sensibles = False

        def resumen(self):
            return ""

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    result = await runner_mod.run_agent(
        "Necesito asesoría sobre un arrendamiento habitacional.",
        channel="web",
        session_id="web:fase0-oos-civil",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "fuera_alcance_materia"
    text = result["text"].lower()
    assert "profesional experto" in text
    assert "animales" not in text
    assert "puedo orient" not in text
    assert "TriageResult" not in result["text"]

@pytest.mark.asyncio
async def test_plan_required_sets_offer_plan(monkeypatch):
    from src.agents import runner as runner_mod

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, *a, **k):
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:fase0-plan"
        hechos_minimos_confirmados = True
        poder_acreditado = True
        ultima_actuacion_confirmada = True
        radicado = "1234567890123456789"
        partes = [{"rol": "victima", "nombre": "X"}]
        rol_despacho = "apoderado"
        etapa_actual = "indagacion"
        terminos: list = []
        evidencias: list = []
        faltantes: list = []
        involucra_menor = False
        datos_sensibles = False

        def resumen(self):
            return "radicado 123 hechos mínimos poder última actuación partes"

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    result = await runner_mod.run_agent(
        "Redáctame un memorial de impulso con los hechos ya aportados",
        channel="web",
        session_id="web:fase0-plan",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "plan_required"
    assert result.get("offer_plan") is True
    assert "TriageResult" not in result["text"]


def test_plan_steps_have_human_summary_not_schema_jargon(monkeypatch):
    from src.agents import planner as planner_mod
    from src.storage.models import Expediente

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def get_expediente(self, _sid):
            return Expediente(
                session_id=_sid,
                hechos_minimos_confirmados=True,
                poder_acreditado=True,
                ultima_actuacion_confirmada=True,
                radicado="1234567890123456789",
                partes=[{"rol": "victima", "nombre": "X"}],
                rol_despacho="apoderado",
            )

        def save_execution_plan(self, record):
            return record

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(planner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(planner_mod, "persist_verification", lambda *a, **k: None)

    plan, err = create_execution_plan(
        message="Redáctame un memorial de impulso",
        channel="web",
        session_id="web:fase0-plan-ui",
        user_id="abogada",
    )
    assert err is None
    assert plan is not None
    blob = " ".join(
        [
            plan.objective,
            *[s.user_summary for s in plan.steps],
            *[s.title for s in plan.steps],
        ]
    )
    assert "TriageResult" not in blob
    assert "EXPEDIENTE INCOMPLETO" not in plan.objective


def test_chat_js_is_chat_first_and_hides_plan_io():
    js = Path("static/chat.js").read_text(encoding="utf-8")
    assert 'authFetch("/chat"' in js
    assert "offer_plan" in js
    assert "Entrada:" not in js
    assert "Salida:" not in js
    # Plan solo tras offer_plan / plan_required
    assert 'authFetch("/chat/plan"' in js

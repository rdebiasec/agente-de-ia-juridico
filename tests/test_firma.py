"""Tests de la firma virtual: esquemas, expediente y roster de agentes."""

import pytest
from pydantic import ValidationError

from src.agents.schemas import ConceptoJuridico, Memorial, Parte
from src.gateway.expediente import ExpedienteStore


def test_memorial_requiere_radicado():
    with pytest.raises(ValidationError):
        Memorial(
            destinatario="Juzgado Penal del Circuito",
            nombre_proceso="Proceso X",
            partes=[Parte(nombre="Cliente", rol="victima")],
            radicado="   ",
            tipo_memorial="impulso procesal",
            peticion="Solicito impulso.",
        )



def test_concepto_valido():
    concepto = ConceptoJuridico(
        cliente="ACME S.A.S.",
        problema_juridico="Riesgos de revictimización en audiencia preliminar.",
        normas_aplicables=["Ley 906 de 2004"],
        conclusion="Se requieren medidas de protección reforzadas para la víctima.",
        recomendacion="Solicitar medidas de protección y plan de acompañamiento.",
    )
    assert concepto.cliente == "ACME S.A.S."


def test_expediente_store_actualiza_por_sesion():
    store = ExpedienteStore()
    exp = store.update("web:abc", materia="penal", etapa_actual="imputación")
    assert exp.materia == "penal"
    assert exp.etapa_actual == "imputación"
    assert "penal" in store.get("web:abc").resumen().lower()


def test_orquestador_tiene_roster_completo():
    from src.agents.orchestrator import SPECIALIST_AGENT_IDS, build_orchestrator

    orquestador = build_orchestrator()
    assert orquestador.name == "coordinador_caso"
    handoffs = getattr(orquestador, "handoffs", None) or []
    assert len(handoffs) == 0
    tool_names = {getattr(t, "name", "") for t in (orquestador.tools or [])}
    assert SPECIALIST_AGENT_IDS.issubset(tool_names)
    assert len(SPECIALIST_AGENT_IDS) == 9


@pytest.mark.asyncio
async def test_run_agent_other_team_scope_queda_en_gerente():
    """Materias de otro equipo Lexiatek quedan en el Gerente, fuera de alcance."""
    from src.agents import runner as runner_mod
    from src.agents.triage import infer_destination_agent

    msg = "Evalúe procedencia de tutela por vulneración de derecho fundamental"
    assert infer_destination_agent(msg) == "coordinador_caso"
    result = await runner_mod.run_agent(
        msg,
        channel="web",
        session_id="web:poc-voice-test",
        user_id="poc-voice-test",
    )
    assert result["agent"] in {"coordinador_caso", "guardrail"}
    assert result["trace"].get("sent_to_agent") in {None, "none", "coordinador_caso"}
    dest = (result["trace"].get("gerencia_verification") or {}).get("destination")
    if dest:
        assert dest == "coordinador_caso"
    text = (result.get("text") or "").lower()
    assert "fuera" in text or "alcance" in text or "penal" in text


def test_ensure_poc_voice_envuelve_especialista_residual():
    from src.agents.runner import _ensure_poc_voice

    wrapped = _ensure_poc_voice(
        "Hallazgo interno de tipicidad.",
        last_agent_name="analista_responsabilidad_tipicidad",
        backoffice_agent="analista_responsabilidad_tipicidad",
    )
    assert wrapped.lower().startswith("como coordinador del caso")
    assert "Hallazgo interno de tipicidad." in wrapped
    assert (
        _ensure_poc_voice(
            "Respuesta del POC.",
            last_agent_name="coordinador_caso",
            backoffice_agent="redactor_documentos_juridicos",
        )
        == "Respuesta del POC."
    )

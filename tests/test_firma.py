"""Tests de la firma virtual: esquemas, expediente y roster de agentes."""

import pytest
from pydantic import ValidationError

from src.agents.schemas import ConceptoJuridico, Memorial, Parte, Tutela
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


def test_tutela_requiere_derecho_vulnerado():
    with pytest.raises(ValidationError):
        Tutela(
            accionante=Parte(nombre="Juan", rol="accionante"),
            accionado=Parte(nombre="EPS", rol="accionado"),
            derecho_vulnerado="",
            fundamentos="Art. 86 C.P.",
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
    assert orquestador.name == "coordinador_expediente_penal"
    handoffs = getattr(orquestador, "handoffs", None) or []
    assert len(handoffs) == 0
    tool_names = {getattr(t, "name", "") for t in (orquestador.tools or [])}
    assert SPECIALIST_AGENT_IDS.issubset(tool_names)
    assert len(SPECIALIST_AGENT_IDS) == 10


@pytest.mark.asyncio
async def test_run_agent_voz_poc_conserva_backoffice_en_traza():
    """Cara al abogado = POC; especialista queda en traza (sent_to_agent)."""
    from src.agents import runner as runner_mod
    from src.agents.orchestrator import POC_AGENT_ID

    result = await runner_mod.run_agent(
        "Evalúe procedencia de tutela por vulneración de derecho fundamental",
        channel="web",
        session_id="web:poc-voice-test",
        user_id="poc-voice-test",
    )
    assert result["agent"] == POC_AGENT_ID
    assert result["trace"]["sent_to_agent"] == "evaluador_derechos_fundamentales_tutela"
    assert result["trace"].get("selected_agent") in {
        "evaluador_derechos_fundamentales_tutela",
        "fallback",
    }


def test_ensure_poc_voice_envuelve_especialista_residual():
    from src.agents.runner import _ensure_poc_voice

    wrapped = _ensure_poc_voice(
        "Hallazgo interno de tipicidad.",
        last_agent_name="analista_tipicidad_y_responsabilidad_penal",
        backoffice_agent="analista_tipicidad_y_responsabilidad_penal",
    )
    assert wrapped.lower().startswith("como coordinador del expediente")
    assert "Hallazgo interno de tipicidad." in wrapped
    assert (
        _ensure_poc_voice(
            "Respuesta del POC.",
            last_agent_name="coordinador_expediente_penal",
            backoffice_agent="redactor_documentos_juridicos_penales",
        )
        == "Respuesta del POC."
    )

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
    from src.agents.orchestrator import build_orchestrator

    orquestador = build_orchestrator()
    assert orquestador.name == "coordinador_expediente_penal"
    assert len(orquestador.handoffs) == 10

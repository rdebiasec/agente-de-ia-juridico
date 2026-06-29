"""Tests de la firma virtual: esquemas, expediente y roster de agentes."""

import pytest
from pydantic import ValidationError

from src.agents.schemas import ConceptoJuridico, Memorial, Parte, Tutela
from src.gateway.expediente import ExpedienteStore


def test_memorial_requiere_radicado():
    with pytest.raises(ValidationError):
        Memorial(
            destinatario="Juzgado 1 Civil",
            nombre_proceso="Proceso X",
            partes=[Parte(nombre="Cliente", rol="demandante")],
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
        problema_juridico="Validez de cláusula de exclusividad.",
        normas_aplicables=["Código de Comercio"],
        conclusion="La cláusula es válida con límites.",
        recomendacion="Ajustar duración y alcance.",
    )
    assert concepto.cliente == "ACME S.A.S."


def test_expediente_store_actualiza_por_sesion():
    store = ExpedienteStore()
    exp = store.update("web:abc", materia="civil", etapa_actual="contestación")
    assert exp.materia == "civil"
    assert exp.etapa_actual == "contestación"
    assert "civil" in store.get("web:abc").resumen().lower()


def test_orquestador_tiene_roster_completo():
    from src.agents.orchestrator import build_orchestrator

    orquestador = build_orchestrator()
    assert orquestador.name == "orquestador"
    assert len(orquestador.handoffs) == 10

"""Tests de la firma virtual: esquemas, expediente y roster de agentes."""

import pytest
from pydantic import ValidationError

from src.agents.agent_names import (
    AGENTE_CIVIL_AUDIENCIA_INICIAL,
    AGENTE_CIVIL_CONTESTACION,
    AGENTE_CIVIL_DEMANDA,
    AGENTE_CIVIL_EJECUCION,
    AGENTE_CIVIL_INSTRUCCION,
    AGENTE_CIVIL_PRUEBA,
    AGENTE_CIVIL_RECURSOS,
    AGENTE_COORDINADOR_CIVIL,
    AGENTE_COORDINADOR_PENAL,
    AGENTE_COORDINADOR_PRINCIPAL,
    SUBAGENTE_INVESTIGACION_VICTIMA,
    SUBAGENTE_PENAL_GARANTIAS,
    SUBAGENTE_PENAL_JUICIOS,
    SUBAGENTE_PENAL_NEGOCIACION,
    SUBAGENTE_PENAL_PRUEBAS,
    SUBAGENTE_PENAL_REPARACION,
    SUBAGENTE_PENAL_RECURSOS,
)
from src.agents.schemas import (
    ConceptoJuridico,
    DenunciaVictima,
    Memorial,
    MemorialReparacionIntegral,
    Parte,
    RubroReparacion,
    Tutela,
)
from src.gateway.expediente import ExpedienteStore
from src.mcp.civil_tools import infer_civil_specialist, infer_etapa_civil
from src.mcp.penal_tools import infer_etapa_penal, infer_penal_specialist


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
    from src.storage.memory import InMemoryRepository

    store = ExpedienteStore(repo=InMemoryRepository())
    exp = store.update("web:abc", materia="civil", etapa_actual="contestación")
    assert exp.materia == "civil"
    assert exp.etapa_actual == "contestación"
    assert "civil" in store.get("web:abc").resumen().lower()


def test_coordinador_principal_tiene_roster_completo():
    from src.agents.orchestrator import build_orchestrator

    coord = build_orchestrator()
    assert coord.name == AGENTE_COORDINADOR_PRINCIPAL
    assert len(coord.handoffs) == 10
    names = {h.agent_name for h in coord.handoffs}
    assert AGENTE_COORDINADOR_CIVIL in names
    assert AGENTE_COORDINADOR_PENAL in names


def test_coordinador_penal_tiene_siete_subagentes():
    from src.agents.penal_orchestrator import build_agente_coordinador_penal

    coord = build_agente_coordinador_penal()
    assert coord.name == AGENTE_COORDINADOR_PENAL
    assert len(coord.handoffs) == 7
    names = {h.agent_name for h in coord.handoffs}
    assert names == {
        SUBAGENTE_INVESTIGACION_VICTIMA,
        SUBAGENTE_PENAL_GARANTIAS,
        SUBAGENTE_PENAL_JUICIOS,
        SUBAGENTE_PENAL_PRUEBAS,
        SUBAGENTE_PENAL_REPARACION,
        SUBAGENTE_PENAL_NEGOCIACION,
        SUBAGENTE_PENAL_RECURSOS,
    }


def test_coordinador_civil_tiene_siete_agentes():
    from src.agents.civil_orchestrator import build_agente_coordinador_civil

    coord = build_agente_coordinador_civil()
    assert coord.name == AGENTE_COORDINADOR_CIVIL
    assert len(coord.handoffs) == 7
    names = {h.agent_name for h in coord.handoffs}
    assert names == {
        AGENTE_CIVIL_DEMANDA,
        AGENTE_CIVIL_CONTESTACION,
        AGENTE_CIVIL_AUDIENCIA_INICIAL,
        AGENTE_CIVIL_INSTRUCCION,
        AGENTE_CIVIL_PRUEBA,
        AGENTE_CIVIL_RECURSOS,
        AGENTE_CIVIL_EJECUCION,
    }


def test_infer_penal_specialist_routes():
    assert infer_penal_specialist("necesito denuncia ante fiscalía") == SUBAGENTE_INVESTIGACION_VICTIMA
    assert infer_penal_specialist("audiencia de imputación") == SUBAGENTE_PENAL_GARANTIAS
    assert infer_penal_specialist("preparar juicio oral") == SUBAGENTE_PENAL_JUICIOS
    assert infer_penal_specialist("matriz de prueba testigo") == SUBAGENTE_PENAL_PRUEBAS
    assert infer_penal_specialist("reparación integral daño moral") == SUBAGENTE_PENAL_REPARACION
    assert infer_penal_specialist("evaluar preacuerdo") == SUBAGENTE_PENAL_NEGOCIACION
    assert infer_penal_specialist("recurso de apelación") == SUBAGENTE_PENAL_RECURSOS


def test_infer_civil_specialist_routes():
    assert infer_civil_specialist("presentar demanda civil") == AGENTE_CIVIL_DEMANDA
    assert infer_civil_specialist("contestación y excepciones") == AGENTE_CIVIL_CONTESTACION
    assert infer_civil_specialist("audiencia inicial art 372") == AGENTE_CIVIL_AUDIENCIA_INICIAL
    assert infer_civil_specialist("audiencia de instrucción 373") == AGENTE_CIVIL_INSTRUCCION
    assert infer_civil_specialist("matriz de prueba testigo") == AGENTE_CIVIL_PRUEBA
    assert infer_civil_specialist("recurso de apelación civil") == AGENTE_CIVIL_RECURSOS
    assert infer_civil_specialist("ejecución de sentencia embargo") == AGENTE_CIVIL_EJECUCION


def test_detectar_etapa_penal():
    assert infer_etapa_penal("imputación ante juez de garantías", "") == "garantias"


def test_detectar_etapa_civil():
    assert infer_etapa_civil("contestación de la demanda", "") == "contestacion"


def test_denuncia_victima_schema():
    denuncia = DenunciaVictima(
        victimas=[Parte(nombre="María López", rol="víctima")],
        delito_presunto="Hurto calificado",
        hechos=["El 1 de enero se sustrajeron bienes."],
    )
    assert denuncia.delito_presunto == "Hurto calificado"


def test_expediente_sync_fija_rol_victima_en_penal():
    from src.services import expediente_sync
    from src.storage.memory import InMemoryRepository

    store = ExpedienteStore(repo=InMemoryRepository())
    original = expediente_sync.expediente_store
    expediente_sync.expediente_store = store
    try:
        result = expediente_sync.sync_expediente_from_chat(
            "web:penal1",
            "Asunto penal ante Fiscalía por hurto",
            [],
        )
        exp = store.get("web:penal1")
        assert exp.materia == "penal"
        assert exp.rol_despacho == "victima"
        assert "rol_despacho=victima" in result["cambios"]
    finally:
        expediente_sync.expediente_store = original


def test_memorial_reparacion_integral_schema():
    memorial = MemorialReparacionIntegral(
        destinatario="Juzgado 5 Penal",
        radicado="12345-2024-00123",
        victimas=[Parte(nombre="María López", rol="víctima")],
        rubros=[
            RubroReparacion(
                nombre="daño emergente",
                descripcion="Gastos médicos",
                prueba_necesaria="Facturas y historia clínica",
            )
        ],
        fundamentos="Normas de reparación integral en KB del despacho.",
        pretensiones=["Condena en abstracto y liquidación"],
    )
    assert memorial.radicado == "12345-2024-00123"

"""L03 — Structured output: schemas de especialistas + render HITL; POC en prosa."""

from __future__ import annotations

import pytest
from pydantic import ValidationError


def test_all_specialists_have_output_type_except_poc():
    from src.agents.orchestrator import POC_AGENT_ID, SPECIALIST_AGENT_IDS, get_agent_by_id

    for agent_id in SPECIALIST_AGENT_IDS:
        agent = get_agent_by_id(agent_id)
        assert agent is not None
        assert agent.output_type is not None, f"falta output_type: {agent_id}"

    poc = get_agent_by_id(POC_AGENT_ID)
    assert poc is not None
    assert getattr(poc, "output_type", None) is None


def test_new_schemas_require_core_fields():
    from src.agents.schemas import (
        PreparacionAudiencia,
        RepresentacionVictimas,
        RutaProcesalLey906,
        SeguimientoProcesal,
    )

    ruta = RutaProcesalLey906(
        resumen="Impulso en indagación",
        etapa_ley906="indagacion_investigacion",
        etapa_aparente="indagacion",
        evidencia_etapa="Denuncia SPOA — fecha narrada",
        fuentes_kb=["agente/conocimiento/proceso-penal-906.md"],
    )
    assert ruta.pendientes_verificacion == []
    assert ruta.etapa_ley906 == "indagacion_investigacion"
    with pytest.raises(ValidationError):
        RutaProcesalLey906(resumen=" ")

    vict = RepresentacionVictimas(teoria_caso="Víctima busca verdad y reparación")
    assert "verdad" in vict.teoria_caso.lower()
    with pytest.raises(ValidationError):
        RepresentacionVictimas(teoria_caso="")

    aud = PreparacionAudiencia(objetivo_audiencia="Solicitar medidas de protección")
    assert aud.guion_puntos == []
    with pytest.raises(ValidationError):
        PreparacionAudiencia(objetivo_audiencia="   ")

    seg = SeguimientoProcesal(resumen="Sin actuaciones recientes")
    assert "[PENDIENTE" in seg.radicado_o_referencia or seg.radicado_o_referencia
    with pytest.raises(ValidationError):
        SeguimientoProcesal(resumen="")


def test_render_new_schemas_is_prose_not_raw_json():
    from src.agents.schemas import (
        PreparacionAudiencia,
        RepresentacionVictimas,
        RutaProcesalLey906,
        SeguimientoProcesal,
    )
    from src.agents.structured_render import render_structured_output

    ruta_txt = render_structured_output(
        RutaProcesalLey906(
            resumen="Evaluar impulso",
            etapa_ley906="indagacion_investigacion",
            etapa_aparente="indagacion",
            evidencia_etapa="Última actuación: denuncia",
            ruta_recomendada=["Solicitar impulso", "Verificar radicado"],
            ruta_detallada=["1. Impulso — abogado — ESTIMACIÓN IA"],
            fuentes_kb=["agente/conocimiento/proceso-penal-906.md"],
            pendientes_verificacion=["Confirmar número SPOA"],
        )
    )
    assert "Ruta procesal" in ruta_txt
    assert "indagacion_investigacion" in ruta_txt
    assert "Solicitar impulso" in ruta_txt
    assert "Confirmar número SPOA" in ruta_txt
    assert "proceso-penal-906.md" in ruta_txt
    assert "'ruta_recomendada'" not in ruta_txt  # no dump dict crudo tipico

    vict_txt = render_structured_output(
        RepresentacionVictimas(
            teoria_caso="Hechos de violencia intrafamiliar",
            derechos_relevantes=["integridad", "acceso a la justicia"],
            riesgos_revictimizacion=["Declaraciones reiteradas"],
        )
    )
    assert "Teoría del caso" in vict_txt
    assert "integridad" in vict_txt

    aud_txt = render_structured_output(
        PreparacionAudiencia(
            objetivo_audiencia="Medidas de protección",
            preguntas_clave=["¿Hay riesgo actual?"],
            checklist=["Poder", "Denuncia"],
        )
    )
    assert "Preparación de audiencia" in aud_txt
    assert "Medidas de protección" in aud_txt

    seg_txt = render_structured_output(
        SeguimientoProcesal(
            resumen="Caso quieto 60 días",
            actuaciones_relevantes=["Denuncia 2024-01"],
            proximas_acciones=["Derecho de petición a Fiscalía"],
            terminos_alertas=["Revisar términos de impulso"],
        )
    )
    assert "Seguimiento procesal" in seg_txt
    assert "Derecho de petición" in seg_txt


def test_redactor_schema_still_valid():
    from src.agents.schemas import BorradorDocumentoPenal
    from src.agents.structured_render import render_structured_output

    draft = BorradorDocumentoPenal(
        tipo="memorial",
        titulo="Impulso",
        cuerpo="Solicito impulso del radicado…",
        pendientes_verificacion=["Confirmar radicado"],
    )
    text = render_structured_output(draft)
    assert "Impulso" in text
    assert "Confirmar radicado" in text
    assert draft.tipo == "memorial"


def test_orchestrator_poc_chat_has_no_output_type():
    from src.agents.orchestrator import POC_AGENT_ID, build_orchestrator

    poc = build_orchestrator(use_cache=False)
    assert poc.name == POC_AGENT_ID
    assert getattr(poc, "output_type", None) is None


def test_matriz_tipicidad_cronologia_y_evidencia_fuentes_kb():
    from src.agents.schemas import (
        CronologiaPenal,
        ElementoTipoPenal,
        EventoCronologia,
        InventarioEvidencia,
        ItemEvidencia,
        MatrizTipicidad,
    )
    from src.agents.structured_render import render_structured_output

    matriz = MatrizTipicidad(
        hipotesis_tipica="Lesiones personales preliminares",
        elementos=[
            ElementoTipoPenal(
                elemento="resultado lesión",
                estado="vacio",
                riesgo_o_brecha="Falta pericia",
            )
        ],
        fuentes_kb=["agente/conocimiento/penal.md"],
    )
    txt = render_structured_output(matriz)
    assert "NO IMPUTACIÓN" in matriz.etiqueta_preliminar
    assert "penal.md" in txt
    assert "[vacio]" in txt

    crono = CronologiaPenal(
        eventos=[
            EventoCronologia(
                fecha_o_momento="2024-01",
                descripcion="Golpe narrado",
                clasificacion="narrado",
                fuente="relato víctima",
            )
        ],
        fuentes_kb=["expediente"],
        vacios_factuales=["Hora exacta"],
    )
    crono_txt = render_structured_output(crono)
    assert "Hora exacta" in crono_txt
    assert crono.fuentes_kb == ["expediente"]

    inv = InventarioEvidencia(
        items=[
            ItemEvidencia(
                descripcion="Fotos de lesiones",
                tipo="digital",
                fuente_o_ubicacion="chat WhatsApp — pendiente hash",
                cadena_custodia="pendiente_verificar",
            )
        ],
        brechas_probatorias=["Falta dictamen médico"],
        plan_recaudo_sugerido=["Solicitar pericia médico-legal"],
        fuentes_kb=["agente/conocimiento/proceso-penal-906.md"],
        pendientes_verificacion=["Hash e integridad del chat"],
    )
    inv_txt = render_structured_output(inv)
    assert "Fotos de lesiones" in inv_txt
    assert "proceso-penal-906.md" in inv_txt
    assert "Falta dictamen médico" in inv_txt
    assert inv.fuentes_kb[0].endswith("proceso-penal-906.md")

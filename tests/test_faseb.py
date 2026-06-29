"""Fase B: persistencia, términos, HITL y documentos."""

from __future__ import annotations

from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient

from src.hitl import drafts as hitl
from src.hitl.drafts import TransicionInvalida
from src.hitl.slack_review import notificar_borrador, slack_habilitado
from src.main import app
from src.services.documentos import extraer_texto, generar_docx
from src.services.plazos import crear_termino, es_dia_habil, sumar_dias_habiles, termino_fallo_tutela
from src.storage.memory import InMemoryRepository
from src.storage.models import (
    ESTADO_APROBADO,
    ESTADO_PROPUESTO,
    ESTADO_RECHAZADO,
    Draft,
)


# --- Términos / plazos ---
def test_dia_habil_excluye_fin_de_semana_y_festivo():
    assert es_dia_habil(date(2026, 2, 6)) is True  # viernes
    assert es_dia_habil(date(2026, 2, 7)) is False  # sábado
    assert es_dia_habil(date(2026, 1, 1)) is False  # Año Nuevo (festivo CO)


def test_sumar_dias_habiles_salta_fin_de_semana():
    base = date(2026, 2, 6)  # viernes
    assert base.weekday() == 4
    assert sumar_dias_habiles(base, 1) == date(2026, 2, 9)  # lunes
    assert sumar_dias_habiles(base, 0) == base


def test_termino_tutela_es_pendiente_con_fecha_limite():
    term = termino_fallo_tutela("web:user", fecha_base=date(2026, 2, 6))
    assert term.dias_habiles == 10
    assert term.estado == "pendiente"
    assert term.fecha_limite is not None and term.fecha_limite > term.fecha_base


def test_crear_termino_calcula_limite():
    term = crear_termino(
        session_id="s", descripcion="Traslado", dias_habiles=3, fecha_base=date(2026, 2, 6)
    )
    assert term.fecha_limite == sumar_dias_habiles(date(2026, 2, 6), 3)


# --- Repositorio en memoria ---
def test_repositorio_memoria_crud_drafts():
    repo = InMemoryRepository()
    draft = repo.add_draft(Draft(session_id="s", tipo="memorial", contenido="x"))
    assert repo.get_draft(draft.id) is not None
    assert len(repo.list_drafts(estado=ESTADO_PROPUESTO)) == 1
    repo.update_draft(draft.id, estado=ESTADO_APROBADO)
    assert repo.get_draft(draft.id).estado == ESTADO_APROBADO
    assert repo.list_drafts(estado=ESTADO_PROPUESTO) == []


# --- HITL: máquina de estados ---
def test_hitl_aprobar_borrador():
    repo = InMemoryRepository()
    draft = hitl.crear_borrador(session_id="s", contenido="Memorial...", tipo="memorial", repo=repo)
    assert draft.estado == ESTADO_PROPUESTO
    aprobado = hitl.aprobar(draft.id, revisor="abogado", repo=repo)
    assert aprobado.estado == ESTADO_APROBADO
    assert aprobado.revisor == "abogado"


def test_hitl_rechazar_y_transicion_invalida():
    repo = InMemoryRepository()
    draft = hitl.crear_borrador(session_id="s", contenido="x", repo=repo)
    hitl.rechazar(draft.id, revisor="abogado", comentario="No aplica", repo=repo)
    with pytest.raises(TransicionInvalida):
        hitl.aprobar(draft.id, revisor="abogado", repo=repo)


def test_hitl_editar_actualiza_contenido():
    repo = InMemoryRepository()
    draft = hitl.crear_borrador(session_id="s", contenido="v1", repo=repo)
    editado = hitl.editar(draft.id, revisor="abogado", nuevo_contenido="v2 corregido", repo=repo)
    assert editado.estado == "editado"
    assert editado.contenido == "v2 corregido"


# --- Slack (no-op sin token) ---
def test_slack_notificacion_noop_sin_token(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "")
    from src.config import get_settings

    get_settings.cache_clear()
    assert slack_habilitado() is False
    assert notificar_borrador(Draft(session_id="s", contenido="x")) is None


# --- Documentos ---
def test_generar_docx_y_extraer_texto_roundtrip():
    data = generar_docx("Memorial de prueba", cuerpo="Señor Juez\n\nComedidamente solicito.")
    assert data[:2] == b"PK"  # firma ZIP/.docx
    texto = extraer_texto("memorial.docx", data)
    assert "Comedidamente solicito" in texto


def test_extraer_texto_formato_no_soportado():
    with pytest.raises(ValueError):
        extraer_texto("imagen.png", b"\x00\x01")


# --- Endpoints HITL ---
@pytest.mark.asyncio
async def test_bandeja_y_aprobacion_endpoints():
    draft = hitl.crear_borrador(session_id="web:endpoint", contenido="Concepto...", tipo="concepto")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pend = await client.get("/drafts/pendientes")
        assert pend.status_code == 200
        ids = [d["id"] for d in pend.json()["drafts"]]
        assert draft.id in ids

        ap = await client.post(f"/drafts/{draft.id}/approve", json={"revisor": "abogado"})
        assert ap.status_code == 200
        assert ap.json()["estado"] == ESTADO_APROBADO

        docx = await client.get(f"/drafts/{draft.id}/docx")
        assert docx.status_code == 200
        assert docx.content[:2] == b"PK"


@pytest.mark.asyncio
async def test_rechazo_transicion_invalida_da_409():
    draft = hitl.crear_borrador(session_id="web:endpoint2", contenido="x", tipo="documento")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(f"/drafts/{draft.id}/reject", json={"comentario": "no"})
        again = await client.post(f"/drafts/{draft.id}/approve", json={})
        assert again.status_code == 409


@pytest.mark.asyncio
async def test_slack_interactivity_sin_config_da_503(monkeypatch):
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "")
    from src.config import get_settings

    get_settings.cache_clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/slack/interactivity", data={"payload": "{}"})
    assert r.status_code == 503

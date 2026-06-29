"""Fase B (parte 2): scheduler de plazos, endpoints de términos, expediente y PDF."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from src.hitl import drafts as hitl
from src.main import app
from src.services.scheduler import clasificar_vencimientos, revisar_plazos
from src.storage.memory import InMemoryRepository
from src.storage.models import Deadline, Expediente


# --- Scheduler (función pura) ---
def _deadline(dias_offset: int, estado: str = "pendiente") -> Deadline:
    return Deadline(
        descripcion=f"t{dias_offset}",
        fecha_limite=date.today() + timedelta(days=dias_offset),
        estado=estado,
    )


def test_clasificar_vencimientos():
    hoy = date.today()
    deadlines = [_deadline(-2), _deadline(1), _deadline(10), _deadline(-1, estado="cumplido")]
    vencidos, proximos = clasificar_vencimientos(deadlines, hoy, dias_aviso=3)
    assert len(vencidos) == 1  # -2 días
    assert len(proximos) == 1  # +1 día (el cumplido y el +10 se excluyen)


def test_revisar_plazos_marca_vencido():
    repo = InMemoryRepository()
    venc = repo.add_deadline(_deadline(-3))
    repo.add_deadline(_deadline(20))
    resumen = revisar_plazos(repo=repo, hoy=date.today())
    assert resumen["vencidos"] == 1
    actualizado = next(d for d in repo.list_deadlines() if d.id == venc.id)
    assert actualizado.estado == "vencido"


# --- Expediente (persistencia repo) ---
def test_expediente_repo_persiste():
    repo = InMemoryRepository()
    repo.save_expediente(Expediente(session_id="web:e1", materia="penal", etapa_actual="imputación"))
    exp = repo.get_expediente("web:e1")
    assert exp is not None
    assert exp.materia == "penal"
    assert "penal" in exp.resumen().lower()


# --- Endpoints de términos ---
@pytest.mark.asyncio
async def test_endpoints_terminos_crear_listar_cumplir():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        crear = await client.post(
            "/deadlines",
            json={"session_id": "web:term", "descripcion": "Traslado", "dias_habiles": 3},
        )
        assert crear.status_code == 200
        tid = crear.json()["id"]
        assert crear.json()["fecha_limite"]

        listar = await client.get("/deadlines", params={"session_id": "web:term"})
        assert any(d["id"] == tid for d in listar.json()["deadlines"])

        patch = await client.patch(f"/deadlines/{tid}", json={"estado": "cumplido"})
        assert patch.status_code == 200
        assert patch.json()["estado"] == "cumplido"


@pytest.mark.asyncio
async def test_aprobar_tutela_crea_termino_automatico():
    draft = hitl.crear_borrador(session_id="web:tut", contenido="Tutela...", tipo="tutela")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ap = await client.post(f"/drafts/{draft.id}/approve", json={"revisor": "abogado"})
        assert ap.status_code == 200
        assert "termino_creado" in ap.json()
        terms = await client.get("/deadlines", params={"session_id": "web:tut"})
        assert any(d["tipo"] == "tutela_fallo" for d in terms.json()["deadlines"])


# --- PDF (requiere libs de WeasyPrint) ---
def test_generar_pdf_desde_borrador():
    from src.storage.models import Draft

    try:
        # WeasyPrint carga libs nativas (pango/cairo) al importar; si no están en la
        # ruta por defecto (p. ej. Mac sin DYLD) levanta OSError -> se omite el test.
        from src.services.documentos import generar_pdf_desde_borrador

        data = generar_pdf_desde_borrador(
            Draft(titulo="Memorial", contenido="Señor Juez\n\nSolicito.")
        )
    except (ImportError, OSError) as exc:
        pytest.skip(f"WeasyPrint sin libs de sistema en este entorno: {exc}")
    assert data[:5] == b"%PDF-"

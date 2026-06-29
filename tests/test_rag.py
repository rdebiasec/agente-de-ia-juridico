"""RAG: chunking, embeddings (fallback local), ingesta y recuperación."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services import rag
from src.storage.memory import InMemoryRepository
from src.storage.models import EMBED_DIM, SCOPE_EXPEDIENTE, SCOPE_KB


def test_trocear_texto_largo_y_corto():
    assert rag.trocear("hola mundo") == ["hola mundo"]
    largo = "párrafo. " * 400  # ~3200 chars
    trozos = rag.trocear(largo, size=800, overlap=100)
    assert len(trozos) > 1
    assert all(len(t) <= 900 for t in trozos)


def test_embedding_local_determinista_y_dimension():
    v1 = rag.embed_texto("acción de tutela")
    v2 = rag.embed_texto("acción de tutela")
    assert v1 == v2
    assert len(v1) == EMBED_DIM
    assert rag.embed_texto("otra cosa") != v1


def test_ingesta_y_busqueda_recupera_fragmento_exacto():
    repo = InMemoryRepository()
    rag.ingestar("La caducidad de la acción contractual es de diez años.",
                 scope=SCOPE_KB, fuente="civil.md", repo=repo)
    rag.ingestar("La imputación se realiza ante el juez de control de garantías.",
                 scope=SCOPE_KB, fuente="penal.md", repo=repo)

    resultados = rag.buscar(
        "La caducidad de la acción contractual es de diez años.", incluir_kb=True, k=2, repo=repo
    )
    assert resultados
    assert resultados[0].fuente == "civil.md"
    assert resultados[0].score == pytest.approx(1.0, abs=1e-6)


def test_busqueda_expediente_respeta_alcance():
    repo = InMemoryRepository()
    rag.ingestar_expediente(
        "El demandado confiesa la deuda en el documento adjunto.",
        expediente_id="EXP-1", fuente="contestacion.pdf", repo=repo,
    )
    # Con expediente: se encuentra.
    con_exp = rag.buscar("confiesa la deuda", expediente_id="EXP-1", incluir_kb=False, k=5, repo=repo)
    assert len(con_exp) == 1
    assert con_exp[0].scope == SCOPE_EXPEDIENTE
    # Sin expediente y solo KB: el chunk del expediente no aparece.
    solo_kb = rag.buscar("confiesa la deuda", expediente_id=None, incluir_kb=True, k=5, repo=repo)
    assert solo_kb == []


def test_contexto_para_prompt_formatea_citas():
    repo = InMemoryRepository()
    rag.ingestar("Texto citable de prueba.", scope=SCOPE_KB, fuente="normas-clave.md", repo=repo)
    chunks = rag.buscar("Texto citable de prueba.", k=1, repo=repo)
    ctx = rag.contexto_para_prompt(chunks)
    assert "Fuente 1" in ctx and "normas-clave.md" in ctx


def test_ingestar_kb_directorio_dedup():
    repo = InMemoryRepository()
    primera = rag.ingestar_kb_directorio(repo=repo)
    assert sum(primera.values()) > 0
    segunda = rag.ingestar_kb_directorio(repo=repo)  # sin reindexar
    assert sum(segunda.values()) == 0


@pytest.mark.asyncio
async def test_endpoints_rag_ingest_y_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ing = await client.post("/rag/ingest-kb")
        assert ing.status_code == 200
        body = ing.json()
        assert "total_fragmentos" in body

        sr = await client.post("/rag/search", json={"consulta": "proceso civil", "k": 3})
        assert sr.status_code == 200
        assert "resultados" in sr.json()

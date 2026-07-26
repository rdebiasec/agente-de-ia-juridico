"""RAG: ingesta y recuperación con embeddings sobre el repositorio (pgvector).

- Con `OPENAI_API_KEY` usa embeddings reales (modelo configurable).
- Sin API key usa un embedding local determinista (mismo texto => mismo vector),
  de modo que el pipeline (ingesta + búsqueda exacta) sea verificable offline.

La IA propone y cita; nunca inventa. Las respuestas de los agentes deben
fundamentarse en los fragmentos recuperados.
"""

from __future__ import annotations

import hashlib
import logging
import os
import struct

from src.config import get_settings
from src.storage import Repository, get_repository
from src.storage.models import EMBED_DIM, SCOPE_EXPEDIENTE, SCOPE_KB, DocumentChunk

logger = logging.getLogger(__name__)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
KB_ALLOWED_FILES = {"penal.md", "proceso-penal-906.md", "normas-clave.md"}

# Se pone en True cuando el último embed usó fallback local (calidad degradada).
_last_embed_used_local_fallback = False


def last_embed_used_local_fallback() -> bool:
    return _last_embed_used_local_fallback


def _repo(repo: Repository | None) -> Repository:
    return repo or get_repository()


def _tiene_api_key() -> bool:
    return bool(get_settings().openai_api_key or os.environ.get("OPENAI_API_KEY"))


def _embedding_local(texto: str, dim: int = EMBED_DIM) -> list[float]:
    """Embedding determinista basado en hash (fallback sin API key)."""
    semilla = hashlib.sha256(texto.strip().lower().encode("utf-8")).digest()
    valores: list[float] = []
    contador = 0
    while len(valores) < dim:
        bloque = hashlib.sha256(semilla + contador.to_bytes(4, "big")).digest()
        for i in range(0, len(bloque), 4):
            entero = struct.unpack(">I", bloque[i : i + 4])[0]
            valores.append(entero / 2**32 - 0.5)
        contador += 1
    valores = valores[:dim]
    norma = sum(v * v for v in valores) ** 0.5 or 1.0
    return [v / norma for v in valores]


def embed_textos(textos: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos."""
    global _last_embed_used_local_fallback
    if not textos:
        return []
    if not _tiene_api_key():
        _last_embed_used_local_fallback = True
        logger.warning(
            "RAG embeddings: usando fallback local (sin OPENAI_API_KEY). "
            "La calidad semántica está degradada; configure la API key en producción."
        )
        return [_embedding_local(t) for t in textos]
    try:
        from openai import OpenAI

        client = OpenAI()
        resp = client.embeddings.create(model=get_settings().embedding_model, input=textos)
        _last_embed_used_local_fallback = False
        return [d.embedding for d in resp.data]
    except Exception:
        _last_embed_used_local_fallback = True
        logger.exception(
            "RAG embeddings: fallo OpenAI; activo fallback local. "
            "Revise cuota/red/modelo; la recuperación semántica queda degradada."
        )
        return [_embedding_local(t) for t in textos]


def embed_texto(texto: str) -> list[float]:
    return embed_textos([texto])[0]


def trocear(texto: str, *, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide el texto en fragmentos solapados, respetando límites de párrafo."""
    limpio = (texto or "").strip()
    if not limpio:
        return []
    if len(limpio) <= size:
        return [limpio]

    trozos: list[str] = []
    inicio = 0
    n = len(limpio)
    while inicio < n:
        fin = min(inicio + size, n)
        # Intentar cortar en un salto de párrafo o espacio cercano.
        if fin < n:
            corte = limpio.rfind("\n\n", inicio, fin)
            if corte == -1 or corte <= inicio:
                corte = limpio.rfind(" ", inicio + size - overlap, fin)
            if corte != -1 and corte > inicio:
                fin = corte
        trozos.append(limpio[inicio:fin].strip())
        if fin >= n:
            break
        inicio = max(fin - overlap, inicio + 1)
    return [t for t in trozos if t]


def ingestar(
    texto: str,
    *,
    scope: str,
    fuente: str,
    expediente_id: str | None = None,
    metadata: dict | None = None,
    repo: Repository | None = None,
) -> int:
    """Trocea, embebe y almacena un texto. Devuelve el número de fragmentos."""
    trozos = trocear(texto)
    if not trozos:
        return 0
    vectores = embed_textos(trozos)
    chunks = [
        DocumentChunk(
            scope=scope,
            expediente_id=expediente_id,
            fuente=fuente,
            chunk_text=trozo,
            embedding=vector,
            metadata=metadata or {},
        )
        for trozo, vector in zip(trozos, vectores)
    ]
    return _repo(repo).add_chunks(chunks)


def ingestar_expediente(
    texto: str, *, expediente_id: str, fuente: str, repo: Repository | None = None
) -> int:
    return ingestar(
        texto, scope=SCOPE_EXPEDIENTE, expediente_id=expediente_id, fuente=fuente, repo=repo
    )


def ingestar_kb_texto(texto: str, *, fuente: str, repo: Repository | None = None) -> int:
    return ingestar(texto, scope=SCOPE_KB, fuente=fuente, repo=repo)


def buscar(
    consulta: str,
    *,
    expediente_id: str | None = None,
    incluir_kb: bool = True,
    k: int = 5,
    repo: Repository | None = None,
) -> list[DocumentChunk]:
    vector = embed_texto(consulta)
    return _repo(repo).buscar_similares(
        vector, expediente_id=expediente_id, incluir_kb=incluir_kb, k=k
    )


def ingestar_kb_directorio(*, reindexar: bool = False, repo: Repository | None = None) -> dict[str, int]:
    """Ingesta solo la KB penal-víctimas habilitada para runtime.

    Por defecto omite archivos ya indexados (dedup por fuente). Con
    `reindexar=True` se vuelven a ingestar (no elimina los previos).
    """
    repository = _repo(repo)
    base = get_settings().agente_dir / "conocimiento"
    resultados: dict[str, int] = {}
    if not base.is_dir():
        return resultados
    for archivo in sorted(base.glob("*.md")):
        fuente = archivo.name
        if fuente not in KB_ALLOWED_FILES:
            continue
        if not reindexar and repository.contar_chunks(scope=SCOPE_KB, fuente=fuente) > 0:
            resultados[fuente] = 0
            continue
        texto = archivo.read_text(encoding="utf-8")
        resultados[fuente] = ingestar(texto, scope=SCOPE_KB, fuente=fuente, repo=repository)
    return resultados


def contexto_para_prompt(chunks: list[DocumentChunk], *, max_chars: int = 3000) -> str:
    """Formatea los fragmentos recuperados como contexto citable para el agente."""
    from src.agents.context_security import sanitize_untrusted_context

    if not chunks:
        return "No se encontraron fragmentos relevantes en la base de conocimiento."
    partes: list[str] = []
    total = 0
    for i, chunk in enumerate(chunks, start=1):
        encabezado = f"[Fuente {i}: {chunk.fuente or chunk.scope}]"
        clean, flags = sanitize_untrusted_context(chunk.chunk_text)
        warning = (
            "\n[Contenido con instrucciones sospechosas omitidas]"
            if flags
            else ""
        )
        bloque = f"{encabezado}{warning}\n{clean}"
        if total + len(bloque) > max_chars and partes:
            break
        partes.append(bloque)
        total += len(bloque)
    return "\n\n".join(partes)

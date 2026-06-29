#!/usr/bin/env python3
"""Indexa la base de conocimiento curada (agente/conocimiento/*.md) en el RAG.

Uso (con Postgres/pgvector vía Docker o Render):
    DATABASE_URL=postgresql+psycopg://agente:agente@localhost:5432/agente \
        .venv/bin/python scripts/ingest_kb.py [--reindexar]

Sin DATABASE_URL usa el repositorio en memoria (solo demostrativo: no persiste
entre procesos). Requiere OPENAI_API_KEY para embeddings reales; sin ella se
usa un embedding local determinista.
"""

import sys

from src.services.rag import ingestar_kb_directorio


def main() -> int:
    reindexar = "--reindexar" in sys.argv
    resultados = ingestar_kb_directorio(reindexar=reindexar)
    if not resultados:
        print("No se encontraron archivos de conocimiento para indexar.")
        return 0
    total = 0
    for fuente, n in resultados.items():
        estado = f"{n} fragmentos" if n else "ya indexado (omitido)"
        print(f"  - {fuente}: {estado}")
        total += n
    print(f"OK: {total} fragmentos nuevos indexados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

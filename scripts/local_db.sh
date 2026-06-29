#!/usr/bin/env bash
# Postgres local con paridad prod (pgvector + Alembic).
# Uso: ./scripts/local_db.sh          # solo levanta DB + migraciones
#      ./scripts/local_db.sh --ingest  # además indexa la KB en RAG
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LOCAL_URL="${DATABASE_URL:-postgresql+psycopg://agente:agente@localhost:5432/agente}"

echo "→ Levantando Postgres+pgvector (Docker)..."
docker compose -f deploy/docker-compose.yml up -d db

echo "→ Esperando que la base esté lista..."
for _ in $(seq 1 30); do
  docker exec deploy-db-1 pg_isready -U agente -d agente >/dev/null 2>&1 && break
  sleep 1
done
docker exec deploy-db-1 pg_isready -U agente -d agente

echo "→ Migraciones Alembic..."
PYTHONPATH=. .venv/bin/python -c "
from src.storage.migrate import run_migrations
run_migrations('$LOCAL_URL')
print('OK: esquema al día (0001 + 0002 + vector)')
"

if [[ "${1:-}" == "--ingest" ]]; then
  echo "→ Indexando base de conocimiento (RAG)..."
  DATABASE_URL="$LOCAL_URL" PYTHONPATH=. .venv/bin/python scripts/ingest_kb.py
fi

echo ""
echo "Listo. DATABASE_URL local:"
echo "  $LOCAL_URL"
echo "Verifique: curl -s http://localhost:8000/health  →  \"persistencia\":\"postgres\""

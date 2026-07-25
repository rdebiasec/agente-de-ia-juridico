#!/usr/bin/env bash
# Arranca el servidor web local con dependencia dura de Postgres (Docker).
# Flujo: Docker Desktop → compose db (healthy) → migraciones → portal → uvicorn.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LOCAL_DB_URL="postgresql+psycopg://agente:agente@localhost:5432/agente"

# Carga .env sin expandir $ de hashes PBKDF2 (evita SITE_PASSWORD corrupto).
# shellcheck disable=SC1091
LOAD_DOTENV_PYTHON="${ROOT}/.venv/bin/python"
# shellcheck source=scripts/lib/load_dotenv.sh
source "${ROOT}/scripts/lib/load_dotenv.sh"
load_dotenv "${ROOT}/.env"

if lsof -ti :8000 >/dev/null 2>&1; then
  echo "Puerto 8000 ocupado. Deteniendo proceso anterior..."
  lsof -ti :8000 | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo "→ Dependencia: Postgres Docker (deploy/docker-compose.yml → servicio db)..."
if ! "$ROOT/scripts/local_db.sh"; then
  echo ""
  echo "ERROR: No se pudo levantar Postgres. El servidor local requiere Docker DB"
  echo "       (paridad con producción; no se usa repositorio en memoria)."
  echo "       Abra Docker Desktop y vuelva a ejecutar: ./scripts/start-local.sh"
  exit 1
fi
# Forzar URL local del compose aunque .env apunte a otro host.
export DATABASE_URL="${LOCAL_DB_URL}"

echo "→ Generando portal de auditoría (mismo origen que prod: /auditoria)..."
AUDIT_API_BASE="" "$ROOT/.venv/bin/python" scripts/generar_audit_portal.py

echo "Iniciando asistente jurídico en http://localhost:8000"
echo "  Chat:       http://localhost:8000/abogado"
echo "  Auditoría:  http://localhost:8000/auditoria/"
echo "  Persistencia: Postgres (Docker) — ${DATABASE_URL}"
echo "Ctrl+C para detener (la DB Docker sigue corriendo; para bajarla: (cd deploy && docker compose --env-file /dev/null stop db))."
exec "$ROOT/.venv/bin/python" -m src.main

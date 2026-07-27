#!/usr/bin/env bash
# Servidor local en modo daemon (launchd / KeepAlive).
# - Levanta Postgres Docker + migraciones
# - Regenera portal /auditoria
# - Corre uvicorn en foreground (sin abrir browser)
# Uso manual: ./scripts/serve-local-daemon.sh
# Uso automático: managed by ~/.local/bin/devctl
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LOCAL_DB_URL="postgresql+psycopg://agente:agente@localhost:5432/agente"
LOG_DIR="${DEVCTL_LOG_DIR:-$HOME/Library/Logs/dbx-devctl}"
mkdir -p "$LOG_DIR"

# shellcheck disable=SC1091
source "${ROOT}/scripts/lib/load_dotenv.sh"
load_dotenv "${ROOT}/.env"

export DATABASE_URL="${LOCAL_DB_URL}"
export OPEN_AUDIT_BROWSER=0
export OPEN_AUDIT_BROWSER_PROD=0

echo "[$(date '+%Y-%m-%d %H:%M:%S')] serve-local-daemon: starting in ${ROOT}"

# Si hay un uvicorn ajeno en :8000 (p. ej. start-local.sh interactivo), liberar puerto.
if lsof -tiTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Puerto 8000 ocupado; liberando listener previo..."
  lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill 2>/dev/null || true
  sleep 1
fi

echo "→ Postgres Docker..."
if ! "$ROOT/scripts/local_db.sh"; then
  echo "ERROR: no se pudo levantar Postgres. Abra Docker Desktop (Start at login recomendado)."
  exit 1
fi

echo "→ Generando portal /auditoria..."
AUDIT_API_BASE="" "$ROOT/.venv/bin/python" scripts/generar_audit_portal.py

WATCH_PID=""
cleanup() {
  if [[ -n "${WATCH_PID}" ]]; then
    kill "${WATCH_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ "${CONFIG_FILE_SYNC_WATCH:-1}" != "0" ]]; then
  AUTHOR="${CONFIG_SYNC_AUTHOR:-local.dev@localhost}"
  echo "→ Config watch ON (author=${AUTHOR})"
  "$ROOT/.venv/bin/python" "$ROOT/scripts/watch_config_sync.py" --author "${AUTHOR}" &
  WATCH_PID=$!
fi

echo "→ http://127.0.0.1:8000  (/abogado · /auditoria/)"
exec "$ROOT/.venv/bin/python" -m src.main

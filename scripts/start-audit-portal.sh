#!/usr/bin/env bash
# Build audit portal, serve on :8080, optionally open browser.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${AUDIT_PORTAL_PORT:-8080}"
OPEN_BROWSER="${OPEN_BROWSER:-1}"
ENV_FILE="$ROOT/audit-portal/.env"

if [[ -f "$ENV_FILE" ]]; then
  echo "→ Cargando credenciales desde audit-portal/.env"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${AUDIT_PORTAL_PASSWORD:-}" ]]; then
  if [[ -f "$ROOT/audit-portal/site/auth-config.js" ]]; then
    echo "→ Sin .env: usando auth-config.js de site/ (hash embebido)"
  else
    echo "⚠️  Sin AUDIT_PORTAL_PASSWORD ni auth-config.js — login desactivado."
    echo "   Copie audit-portal/.env.example → audit-portal/.env o defina site/auth-config.js"
  fi
fi

echo "→ Generando audit-portal/dist..."
export AUDIT_API_BASE="${AUDIT_API_BASE:-http://127.0.0.1:8000}"
python3 scripts/generar_audit_portal.py

if lsof -ti ":$PORT" >/dev/null 2>&1; then
  echo "→ Liberando puerto $PORT..."
  lsof -ti ":$PORT" | xargs kill -9 2>/dev/null || true
  sleep 0.5
fi

echo "→ Servidor en http://127.0.0.1:$PORT (Ctrl+C para detener)"
echo "→ API: $AUDIT_API_BASE — inicie FastAPI con ./scripts/start-local.sh si no está activo"
echo "→ Login: correo + SITE_PASSWORD del despacho"
if [[ "$OPEN_BROWSER" == "1" ]] && command -v open >/dev/null 2>&1; then
  (sleep 1 && open "http://127.0.0.1:$PORT/") &
fi

exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory audit-portal/dist

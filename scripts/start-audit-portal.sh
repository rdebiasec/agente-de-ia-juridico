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
  echo "⚠️  Sin AUDIT_PORTAL_PASSWORD — login desactivado en este build."
  echo "   Copie audit-portal/.env.example → audit-portal/.env y defina la contraseña."
fi

echo "→ Generando audit-portal/dist..."
python3 scripts/generar_audit_portal.py

if lsof -ti ":$PORT" >/dev/null 2>&1; then
  echo "→ Liberando puerto $PORT..."
  lsof -ti ":$PORT" | xargs kill -9 2>/dev/null || true
  sleep 0.5
fi

echo "→ Servidor en http://localhost:$PORT (Ctrl+C para detener)"
if [[ "$OPEN_BROWSER" == "1" ]] && command -v open >/dev/null 2>&1; then
  (sleep 1 && open "http://localhost:$PORT/") &
fi

exec python3 -m http.server "$PORT" --directory audit-portal/dist

#!/usr/bin/env bash
# Preview estático del portal en :8080 (cross-origin → API en :8000).
# Para paridad con prod use ./scripts/start-local.sh → http://127.0.0.1:8000/auditoria/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${AUDIT_PORTAL_PORT:-8080}"
OPEN_BROWSER="${OPEN_BROWSER:-1}"

echo "→ Generando audit-portal/dist (cross-origin, como GitHub Pages)..."
export AUDIT_API_BASE="${AUDIT_API_BASE:-http://127.0.0.1:8000}"
python3 scripts/generar_audit_portal.py

if lsof -ti ":$PORT" >/dev/null 2>&1; then
  echo "→ Liberando puerto $PORT..."
  lsof -ti ":$PORT" | xargs kill -9 2>/dev/null || true
  sleep 0.5
fi

echo "→ Servidor en http://127.0.0.1:$PORT (Ctrl+C para detener)"
echo "→ API: $AUDIT_API_BASE — inicie FastAPI con ./scripts/start-local.sh"
echo "→ Login: correo + SITE_PASSWORD del .env raíz"
if [[ "$OPEN_BROWSER" == "1" ]] && command -v open >/dev/null 2>&1; then
  (sleep 1 && open "http://127.0.0.1:$PORT/") &
fi

exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory audit-portal/dist

#!/usr/bin/env bash
# Reconstruye el entorno local (venv, deps, DB, portal). No toca Render.
# Uso: ./scripts/dr/rebuild_local.sh [--ingest] [--start]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
INGEST=0
START=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ingest) INGEST=1; shift ;;
    --start) START=1; shift ;;
    -h|--help)
      echo "Uso: rebuild_local.sh [--ingest] [--start]"
      echo "  --ingest  indexa KB (RAG) tras migraciones"
      echo "  --start   arranca la app al final (start-local.sh)"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: falta .env. Copie .env.example y complete secretos (Runbook E)." >&2
  exit 1
fi

if [[ ! -d "$ROOT/.venv" ]]; then
  echo "→ Creando .venv..."
  python3 -m venv "$ROOT/.venv"
fi

echo "→ Instalando dependencias editable [dev]..."
"$ROOT/.venv/bin/pip" install -q -e ".[dev]"

echo "→ Postgres + migraciones..."
if [[ "$INGEST" -eq 1 ]]; then
  "$ROOT/scripts/local_db.sh" --ingest
else
  "$ROOT/scripts/local_db.sh"
fi

echo "→ Generando audit-portal/dist (mismo origen)..."
AUDIT_API_BASE="" "$ROOT/.venv/bin/python" scripts/generar_audit_portal.py

echo ""
echo "OK: entorno local reconstruido."
echo "  Arranque: ./scripts/start-local.sh"
echo "  Verificar: ./scripts/dr/verify_recovery.sh --local"

if [[ "$START" -eq 1 ]]; then
  exec "$ROOT/scripts/start-local.sh"
fi

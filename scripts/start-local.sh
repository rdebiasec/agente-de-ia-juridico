#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

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

if [[ -f "$ROOT/.env" ]] && grep -qE '^DATABASE_URL=.+' "$ROOT/.env"; then
  echo "→ Postgres en .env: verificando base local..."
  if ! "$ROOT/scripts/local_db.sh"; then
    echo ""
    echo "AVISO: Postgres no disponible (¿Docker Desktop apagado?)."
    echo "       Arrancando en modo memoria — reinicio de chat y chat funcionan,"
    echo "       pero sin persistencia. Para paridad con prod: abra Docker y vuelva a ejecutar."
    echo ""
    export DATABASE_URL=
  fi
fi

echo "→ Generando portal de auditoría (mismo origen que prod: /auditoria)..."
AUDIT_API_BASE="" "$ROOT/.venv/bin/python" scripts/generar_audit_portal.py

echo "Iniciando asistente jurídico en http://localhost:8000"
echo "Chat: http://localhost:8000/abogado"
echo "Auditoría: http://localhost:8000/auditoria/ (login: correo + SITE_PASSWORD del .env)"
echo "Ctrl+C para detener."
exec "$ROOT/.venv/bin/python" -m src.main

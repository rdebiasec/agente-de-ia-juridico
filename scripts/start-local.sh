#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if lsof -ti :8000 >/dev/null 2>&1; then
  echo "Puerto 8000 ocupado. Deteniendo proceso anterior..."
  lsof -ti :8000 | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo "Iniciando asistente jurídico en http://localhost:8000"
echo "Abra esa URL en el navegador para chatear. Ctrl+C para detener."
exec "$ROOT/.venv/bin/python" -m src.main

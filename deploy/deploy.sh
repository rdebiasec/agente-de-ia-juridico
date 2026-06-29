#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Validando estructura de la firma (Fases A+B)..."
python3 scripts/validate_fase0.py

echo "==> Build Docker..."
docker compose -f deploy/docker-compose.yml build

echo "==> Despliegue listo. Ejecute: docker compose -f deploy/docker-compose.yml up"
echo "    Health: http://localhost:8000/health"
echo "    Chat API: POST http://localhost:8000/chat"

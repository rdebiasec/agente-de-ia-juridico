#!/usr/bin/env bash
# Restore Postgres desde dump custom-format (-Fc).
# Uso:
#   ./scripts/dr/restore_postgres.sh ~/Backups/.../agente-....dump
#   ./scripts/dr/restore_postgres.sh --wipe dump.dump
#   DATABASE_URL='postgresql://...' ./scripts/dr/restore_postgres.sh --remote dump.dump
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WIPE=0
REMOTE=0
DUMP=""
CONFIRM="${DR_CONFIRM:-}"

usage() {
  cat <<'EOF'
Uso: restore_postgres.sh [--wipe] [--remote] <archivo.dump>

  Local (default): restaura en contenedor deploy-db-1 (usuario agente / db agente).
  --remote:        usa DATABASE_URL (External URL Render, etc.).
  --wipe:          DROP SCHEMA public CASCADE + CREATE SCHEMA antes de restaurar.

  Confirmación: escriba YES (mayúsculas) o exporte DR_CONFIRM=YES.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wipe) WIPE=1; shift ;;
    --remote) REMOTE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*)
      echo "Opción desconocida: $1" >&2
      usage
      exit 1
      ;;
    *)
      DUMP="$1"
      shift
      ;;
  esac
done

if [[ -z "$DUMP" || ! -f "$DUMP" ]]; then
  echo "ERROR: indique un archivo .dump existente." >&2
  usage
  exit 1
fi

DUMP="$(cd "$(dirname "$DUMP")" && pwd)/$(basename "$DUMP")"

normalize_url() {
  local u="$1"
  u="${u#postgresql+psycopg://}"
  u="${u#postgresql+psycopg2://}"
  if [[ "$u" == postgresql://* ]] || [[ "$u" == postgres://* ]]; then
    echo "$u"
  else
    echo "postgresql://${u}"
  fi
}

EXPECTED_CONFIRM="YES"
if [[ "$REMOTE" -eq 1 ]]; then
  EXPECTED_CONFIRM="RESTORE PRODUCTION"
fi

if [[ -z "$CONFIRM" ]]; then
  echo "Va a restaurar: $DUMP"
  if [[ "$WIPE" -eq 1 ]]; then
    echo "MODO --wipe: se borrará el esquema public antes de restaurar."
  fi
  if [[ "$REMOTE" -eq 1 ]]; then
    echo "Destino: DATABASE_URL remota (producción / staging)."
    echo "PELIGRO: esto puede destruir el progreso de la abogada en prod."
  else
    echo "Destino: Postgres local (deploy-db-1)."
  fi
  read -r -p "Escriba ${EXPECTED_CONFIRM} para continuar: " CONFIRM
fi
if [[ "$CONFIRM" != "$EXPECTED_CONFIRM" ]]; then
  echo "Cancelado (se esperaba: ${EXPECTED_CONFIRM})."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker no disponible." >&2
  exit 1
fi

if [[ "$REMOTE" -eq 1 ]]; then
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "ERROR: DATABASE_URL requerida con --remote." >&2
    exit 1
  fi
  PGURL="$(normalize_url "$DATABASE_URL")"
  BACKUP_DIR="$(dirname "$DUMP")"
  BASE="$(basename "$DUMP")"
  if [[ "$WIPE" -eq 1 ]]; then
    echo "→ Wipe schema remoto..."
    docker run --rm -v "$BACKUP_DIR:/backups" postgres:16 \
      psql "$PGURL" -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
  fi
  echo "→ pg_restore remoto..."
  docker run --rm -v "$BACKUP_DIR:/backups" postgres:16 \
    pg_restore --clean --if-exists --no-owner --no-acl -d "$PGURL" "/backups/$BASE" \
    || true
  # pg_restore puede devolver warnings no fatales; verificar con psql
  docker run --rm postgres:16 psql "$PGURL" -c "SELECT 1" >/dev/null
  echo "OK: restore remoto completado."
  exit 0
fi

# Local
if ! docker exec deploy-db-1 pg_isready -U agente -d agente >/dev/null 2>&1; then
  echo "→ Levantando Postgres local..."
  "$ROOT/scripts/local_db.sh" >/dev/null
fi

docker cp "$DUMP" deploy-db-1:/tmp/restore.dump

if [[ "$WIPE" -eq 1 ]]; then
  echo "→ Wipe schema local..."
  docker exec deploy-db-1 psql -U agente -d agente -v ON_ERROR_STOP=1 \
    -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
fi

echo "→ pg_restore local..."
# --clean puede fallar si no hay objetos; aceptar código no-cero si la DB queda usable
set +e
docker exec deploy-db-1 pg_restore --clean --if-exists --no-owner --no-acl \
  -U agente -d agente /tmp/restore.dump
RC=$?
set -e
docker exec deploy-db-1 rm -f /tmp/restore.dump

docker exec deploy-db-1 psql -U agente -d agente -c "SELECT 1" >/dev/null
echo "→ Aplicando migraciones Alembic (por si el dump es antiguo)..."
"$ROOT/scripts/local_db.sh" >/dev/null
echo "OK: restore local completado (pg_restore exit=$RC)."

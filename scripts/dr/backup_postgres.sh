#!/usr/bin/env bash
# Backup Postgres (local Docker o DATABASE_URL remoto).
# Uso:
#   ./scripts/dr/backup_postgres.sh
#   ./scripts/dr/backup_postgres.sh --label local
#   DATABASE_URL='postgresql://...' ./scripts/dr/backup_postgres.sh --label prod
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$HOME/Backups/agente-juridico/postgres}"
LABEL="local"
STAMP="$(date +%Y%m%d-%H%M)"

usage() {
  cat <<'EOF'
Uso: backup_postgres.sh [--label NAME]

  Sin DATABASE_URL (o apuntando a localhost): dump vía contenedor deploy-db-1.
  Con DATABASE_URL remoto: dump vía imagen postgres:16 (Docker).

Variables:
  BACKUP_DIR   Destino (default ~/Backups/agente-juridico/postgres)
  DATABASE_URL URL SQLAlchemy o libpq (postgresql:// o postgresql+psycopg://)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opción desconocida: $1" >&2; usage; exit 1 ;;
  esac
done

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

is_local_url() {
  local u="$1"
  [[ -z "$u" ]] && return 0
  [[ "$u" == *"localhost"* || "$u" == *"127.0.0.1"* ]] && return 0
  return 1
}

mkdir -p "$BACKUP_DIR"
OUT="${BACKUP_DIR}/agente-${STAMP}-${LABEL}.dump"

# Cargar .env si existe (sin exportar secretos a stdout)
if [[ -f "$ROOT/.env" ]] && [[ -z "${DATABASE_URL:-}" ]]; then
  # shellcheck disable=SC1091
  set -a
  # Solo exportar DATABASE_URL si está definido en .env
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^DATABASE_URL= ]]; then
      export "$line"
    fi
  done < "$ROOT/.env"
  set +a
fi

DB_URL="${DATABASE_URL:-}"

if is_local_url "$DB_URL"; then
  if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker no disponible. Abra Docker Desktop." >&2
    exit 1
  fi
  if ! docker exec deploy-db-1 pg_isready -U agente -d agente >/dev/null 2>&1; then
    echo "→ Levantando Postgres local..."
    "$ROOT/scripts/local_db.sh" >/dev/null
  fi
  echo "→ Dump local (deploy-db-1) → $OUT"
  docker exec deploy-db-1 pg_dump -U agente -d agente -Fc -f /tmp/agente.dump
  docker cp deploy-db-1:/tmp/agente.dump "$OUT"
  docker exec deploy-db-1 rm -f /tmp/agente.dump
else
  if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker requerido para pg_dump remoto (no hay cliente Postgres en el host)." >&2
    exit 1
  fi
  PGURL="$(normalize_url "$DB_URL")"
  echo "→ Dump remoto → $OUT"
  # Montar destino; no imprimir la URL (contiene credenciales)
  docker run --rm \
    -e PGPASSWORD \
    -v "$BACKUP_DIR:/backups" \
    postgres:16 \
    pg_dump "$PGURL" -Fc -f "/backups/$(basename "$OUT")"
fi

SIZE="$(du -h "$OUT" | awk '{print $1}')"
echo "OK: $OUT ($SIZE)"
echo "$OUT"

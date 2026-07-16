#!/usr/bin/env bash
# Backup LOCAL automático: Postgres Docker + auditoría + secrets → R2 (cifrado)
# y copia en ~/Backups/agente-juridico/.
#
# Credenciales: ~/Backups/agente-juridico/backup.env (chmod 600)
# Instalación: ./scripts/dr/install_local_backup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONF="${BACKUP_ENV_FILE:-$HOME/Backups/agente-juridico/backup.env}"
LOG_DIR="${BACKUP_LOG_DIR:-$HOME/Backups/agente-juridico/logs}"
LOCAL_DIR="${BACKUP_LOCAL_DIR:-$HOME/Backups/agente-juridico}"
LABEL="local"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
DAY="$(date -u +%Y%m%d)"
RETAIN_DAYS="${RETAIN_DAYS:-30}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/agente-local-backup.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$LOG_DIR" "$LOCAL_DIR/postgres" "$LOCAL_DIR/audit-progress" "$LOCAL_DIR/secrets"
LOG="$LOG_DIR/local-backup-$(date +%Y%m%d).log"
exec >>"$LOG" 2>&1

echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) backup_local_to_r2 start ====="

if [[ ! -f "$CONF" ]]; then
  echo "ERROR: falta $CONF — ejecute ./scripts/dr/install_local_backup.sh" >&2
  exit 1
fi
# shellcheck disable=SC1090
set -a
source "$CONF"
set +a

require() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "ERROR: $name no definido en $CONF" >&2
    exit 1
  fi
}

require BACKUP_ENCRYPTION_KEY
require R2_ACCOUNT_ID
require R2_ACCESS_KEY_ID
require R2_SECRET_ACCESS_KEY
require R2_BUCKET

# PATH para launchd (Docker Desktop + homebrew)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
# Docker Desktop socket en Mac
export DOCKER_HOST="${DOCKER_HOST:-unix://$HOME/.docker/run/docker.sock}"
if [[ ! -S "${HOME}/.docker/run/docker.sock" ]]; then
  export DOCKER_HOST="unix:///var/run/docker.sock"
fi

cd "$ROOT"

echo "→ verificando Docker / Postgres local"
if ! docker info >/dev/null 2>&1; then
  echo "WARN: Docker no disponible. Reintento en 60s…"
  sleep 60
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker Desktop no responde. Abra Docker y el LaunchAgent reintentará en el próximo ciclo." >&2
  exit 1
fi

if ! docker exec deploy-db-1 pg_isready -U agente -d agente >/dev/null 2>&1; then
  echo "→ levantando Postgres local…"
  "$ROOT/scripts/local_db.sh" >/dev/null || true
  sleep 5
fi
if ! docker exec deploy-db-1 pg_isready -U agente -d agente >/dev/null 2>&1; then
  echo "ERROR: Postgres local (deploy-db-1) no listo." >&2
  exit 1
fi

# DATABASE_URL local desde .env del proyecto
if [[ -f "$ROOT/.env" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    case "$line" in
      DATABASE_URL=*|SITE_USERNAME=*|SITE_PASSWORD=*|SESSION_SECRET=*|OPENAI_API_KEY=*|OPENAI_MODEL=*|EMBEDDING_MODEL=*|SLACK_*=*|TWILIO_*=*|SESSION_*=*|DEV_AUTO_LOGIN=*|AGENT_MAX_TURNS=*|AUDIT_CORS_ORIGINS=*)
        export "$line" 2>/dev/null || true
        ;;
    esac
  done <"$ROOT/.env"
fi
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://agente:agente@localhost:5432/agente}"
export PROD_DATABASE_URL="${DATABASE_URL}"

DUMP_RAW="$WORK/agente-${STAMP}-${LABEL}.dump"
DUMP_ENC="${DUMP_RAW}.gpg"
JSON_RAW="$WORK/audit-progress-${STAMP}-${LABEL}.json"
JSON_ENC="${JSON_RAW}.gpg"
SECRETS_RAW="$WORK/secrets-${STAMP}-${LABEL}.env"
SECRETS_ENC="${SECRETS_RAW}.gpg"

echo "→ pg_dump local"
docker exec deploy-db-1 pg_dump -U agente -d agente -Fc -f /tmp/agente.dump
docker cp deploy-db-1:/tmp/agente.dump "$DUMP_RAW"
docker exec deploy-db-1 rm -f /tmp/agente.dump
cp "$DUMP_RAW" "$LOCAL_DIR/postgres/$(basename "$DUMP_RAW")"

echo "→ export auditoría"
PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then PY=python3; fi
"$PY" "$ROOT/scripts/dr/export_audit_progress.py" --label local --out-dir "$WORK" >/dev/null
JSON_SRC="$(ls -1t "$WORK"/audit-progress-*.json | head -1)"
cp "$JSON_SRC" "$JSON_RAW"
cp "$JSON_RAW" "$LOCAL_DIR/audit-progress/$(basename "$JSON_RAW")"

echo "→ pack secrets locales"
chmod +x "$ROOT/scripts/dr/pack_recovery_secrets.sh"
"$ROOT/scripts/dr/pack_recovery_secrets.sh" "$SECRETS_RAW"
cp "$SECRETS_RAW" "$LOCAL_DIR/secrets/$(basename "$SECRETS_RAW")"
chmod 600 "$LOCAL_DIR/secrets/$(basename "$SECRETS_RAW")"

gpg_enc() {
  gpg --batch --yes --pinentry-mode loopback --symmetric --cipher-algo AES256 \
    --passphrase "$BACKUP_ENCRYPTION_KEY" -o "$2" "$1"
}

echo "→ cifrar"
gpg_enc "$DUMP_RAW" "$DUMP_ENC"
gpg_enc "$JSON_RAW" "$JSON_ENC"
gpg_enc "$SECRETS_RAW" "$SECRETS_ENC"

ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="auto"
export AWS_EC2_METADATA_DISABLED=true

# awscli vía python -m (evita shebang roto si el path del repo tiene espacios)
"$PY" -m pip install -q "awscli>=1.32,<2" >/dev/null 2>&1 || true
aws_s3() {
  "$PY" -m awscli s3 "$@"
}

ENV_ROOT="${R2_ENV_ROOT:-dev}"
echo "→ upload R2 ${ENV_ROOT}/${DAY}/"
aws_s3 cp "$DUMP_ENC" "s3://${R2_BUCKET}/${ENV_ROOT}/postgres/${DAY}/$(basename "$DUMP_ENC")" --endpoint-url "$ENDPOINT"
aws_s3 cp "$JSON_ENC" "s3://${R2_BUCKET}/${ENV_ROOT}/audit-progress/${DAY}/$(basename "$JSON_ENC")" --endpoint-url "$ENDPOINT"
aws_s3 cp "$SECRETS_ENC" "s3://${R2_BUCKET}/${ENV_ROOT}/secrets/${DAY}/$(basename "$SECRETS_ENC")" --endpoint-url "$ENDPOINT"

{
  echo "created_at_utc=${STAMP}"
  echo "label=dev"
  echo "postgres=$(basename "$DUMP_ENC")"
  echo "audit=$(basename "$JSON_ENC")"
  echo "secrets=$(basename "$SECRETS_ENC")"
} | aws_s3 cp - "s3://${R2_BUCKET}/${ENV_ROOT}/LATEST.txt" --endpoint-url "$ENDPOINT"

echo "→ retención local (${RETAIN_DAYS}d) + R2"
find "$LOCAL_DIR/postgres" -type f -name 'agente-*.dump' -mtime +"${RETAIN_DAYS}" -delete 2>/dev/null || true
find "$LOCAL_DIR/audit-progress" -type f -name 'audit-progress-*.json' -mtime +"${RETAIN_DAYS}" -delete 2>/dev/null || true
find "$LOCAL_DIR/secrets" -type f -name 'secrets-*.env' -mtime +"${RETAIN_DAYS}" -delete 2>/dev/null || true

CUTOFF="$(date -u -v-"${RETAIN_DAYS}"d +%Y%m%d 2>/dev/null || date -u -d "-${RETAIN_DAYS} days" +%Y%m%d)"
for prefix in "${ENV_ROOT}/postgres" "${ENV_ROOT}/audit-progress" "${ENV_ROOT}/secrets"; do
  aws_s3 ls "s3://${R2_BUCKET}/${prefix}/" --endpoint-url "$ENDPOINT" 2>/dev/null \
    | awk '{print $2}' | sed 's:/$::' | while read -r daydir; do
      [[ "$daydir" =~ ^[0-9]{8}$ ]] || continue
      if [[ "$daydir" < "$CUTOFF" ]]; then
        aws_s3 rm "s3://${R2_BUCKET}/${prefix}/${daydir}/" --recursive --endpoint-url "$ENDPOINT" || true
      fi
    done
done

echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) backup_local_to_r2 OK ====="

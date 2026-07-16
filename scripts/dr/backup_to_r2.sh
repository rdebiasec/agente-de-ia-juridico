#!/usr/bin/env bash
# Backup completo → cifrado GPG → Cloudflare R2.
# Incluye: Postgres dump, progreso auditoría JSON, secrets.env de recuperación.
#
# Requiere:
#   DATABASE_URL / PROD_DATABASE_URL
#   BACKUP_ENCRYPTION_KEY
#   R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
#   + variables de app (SITE_PASSWORD, OPENAI_API_KEY, …) para el paquete de secretos
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="${LABEL:-prod}"
RETAIN_DAYS="${RETAIN_DAYS:-30}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
DAY="$(date -u +%Y%m%d)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/agente-backup.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

require() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "ERROR: falta variable de entorno $name" >&2
    exit 1
  fi
}

# Aceptar DATABASE_URL o PROD_DATABASE_URL
if [[ -z "${DATABASE_URL:-}" && -n "${PROD_DATABASE_URL:-}" ]]; then
  DATABASE_URL="$PROD_DATABASE_URL"
fi
if [[ -z "${PROD_DATABASE_URL:-}" && -n "${DATABASE_URL:-}" ]]; then
  PROD_DATABASE_URL="$DATABASE_URL"
fi
export DATABASE_URL PROD_DATABASE_URL

require DATABASE_URL
require BACKUP_ENCRYPTION_KEY
require R2_ACCOUNT_ID
require R2_ACCESS_KEY_ID
require R2_SECRET_ACCESS_KEY
require R2_BUCKET

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

gpg_enc() {
  local src="$1" dst="$2"
  gpg --batch --yes --pinentry-mode loopback --symmetric --cipher-algo AES256 \
    --passphrase "$BACKUP_ENCRYPTION_KEY" \
    -o "$dst" "$src"
}

PGURL="$(normalize_url "$DATABASE_URL")"
ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="auto"
export AWS_EC2_METADATA_DISABLED=true

DUMP_RAW="$WORK/agente-${STAMP}-${LABEL}.dump"
DUMP_ENC="${DUMP_RAW}.gpg"
JSON_RAW="$WORK/audit-progress-${STAMP}-${LABEL}.json"
JSON_ENC="${JSON_RAW}.gpg"
SECRETS_RAW="$WORK/secrets-${STAMP}-${LABEL}.env"
SECRETS_ENC="${SECRETS_RAW}.gpg"
MANIFEST="$WORK/MANIFEST-${STAMP}-${LABEL}.txt"

echo "→ pg_dump (${LABEL})"
if command -v docker >/dev/null 2>&1; then
  docker run --rm \
    -v "$WORK:/out" \
    postgres:18 \
    pg_dump "$PGURL" -Fc -f "/out/$(basename "$DUMP_RAW")"
else
  pg_dump "$PGURL" -Fc -f "$DUMP_RAW"
fi

echo "→ export audit progress JSON"
DATABASE_URL="$DATABASE_URL" \
  python3 "$ROOT/scripts/dr/export_audit_progress.py" \
  --label "$LABEL" \
  --out-dir "$WORK" >/dev/null
JSON_SRC="$(ls -1t "$WORK"/audit-progress-*.json | head -1)"
cp "$JSON_SRC" "$JSON_RAW"

echo "→ pack recovery secrets"
chmod +x "$ROOT/scripts/dr/pack_recovery_secrets.sh"
"$ROOT/scripts/dr/pack_recovery_secrets.sh" "$SECRETS_RAW"

{
  echo "created_at_utc=${STAMP}"
  echo "label=${LABEL}"
  echo "postgres=$(basename "$DUMP_ENC")"
  echo "audit=$(basename "$JSON_ENC")"
  echo "secrets=$(basename "$SECRETS_ENC")"
  echo "note=Decrypt with BACKUP_ENCRYPTION_KEY from password manager / local Backups file."
} >"$MANIFEST"

echo "→ cifrar con GPG"
gpg_enc "$DUMP_RAW" "$DUMP_ENC"
gpg_enc "$JSON_RAW" "$JSON_ENC"
gpg_enc "$SECRETS_RAW" "$SECRETS_ENC"

echo "→ upload R2 s3://${R2_BUCKET}/"
aws s3 cp "$DUMP_ENC" \
  "s3://${R2_BUCKET}/postgres/${DAY}/$(basename "$DUMP_ENC")" \
  --endpoint-url "$ENDPOINT"
aws s3 cp "$JSON_ENC" \
  "s3://${R2_BUCKET}/audit-progress/${DAY}/$(basename "$JSON_ENC")" \
  --endpoint-url "$ENDPOINT"
aws s3 cp "$SECRETS_ENC" \
  "s3://${R2_BUCKET}/secrets/${DAY}/$(basename "$SECRETS_ENC")" \
  --endpoint-url "$ENDPOINT"
aws s3 cp "$MANIFEST" \
  "s3://${R2_BUCKET}/manifests/${DAY}/$(basename "$MANIFEST")" \
  --endpoint-url "$ENDPOINT"
# Puntero "latest" para recuperación rápida
aws s3 cp "$MANIFEST" \
  "s3://${R2_BUCKET}/LATEST.txt" \
  --endpoint-url "$ENDPOINT"

echo "→ retención: borrar objetos con más de ${RETAIN_DAYS} días"
CUTOFF="$(date -u -d "-${RETAIN_DAYS} days" +%Y%m%d 2>/dev/null || date -u -v-"${RETAIN_DAYS}"d +%Y%m%d)"
for prefix in postgres audit-progress secrets manifests; do
  aws s3 ls "s3://${R2_BUCKET}/${prefix}/" --endpoint-url "$ENDPOINT" \
    | awk '{print $2}' | sed 's:/$::' | while read -r daydir; do
      [[ "$daydir" =~ ^[0-9]{8}$ ]] || continue
      if [[ "$daydir" < "$CUTOFF" ]]; then
        echo "  borrando s3://${R2_BUCKET}/${prefix}/${daydir}/"
        aws s3 rm "s3://${R2_BUCKET}/${prefix}/${daydir}/" --recursive --endpoint-url "$ENDPOINT"
      fi
    done
done

echo "OK: backup completo en R2 (postgres + audit-progress + secrets + LATEST.txt)"

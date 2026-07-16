#!/usr/bin/env bash
# Backup Postgres + progreso auditoría → cifrado GPG → Cloudflare R2.
# Pensado para GitHub Actions (también usable en local con las mismas env vars).
#
# Requiere:
#   DATABASE_URL              External URL Postgres (prod)
#   BACKUP_ENCRYPTION_KEY     Passphrase GPG simétrica
#   R2_ACCOUNT_ID
#   R2_ACCESS_KEY_ID
#   R2_SECRET_ACCESS_KEY
#   R2_BUCKET                 p.ej. agente-juridico-backups
#
# Opcional:
#   RETAIN_DAYS               default 30
#   LABEL                     default prod
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

echo "→ pg_dump (${LABEL})"
# No imprimir PGURL (contiene credenciales)
pg_dump "$PGURL" -Fc -f "$DUMP_RAW"

echo "→ export audit progress JSON"
DATABASE_URL="$DATABASE_URL" \
  python3 "$ROOT/scripts/dr/export_audit_progress.py" \
  --label "$LABEL" \
  --out-dir "$WORK" >/dev/null
# El export escribe con su propio stamp; tomar el JSON más reciente del workdir
JSON_SRC="$(ls -1t "$WORK"/audit-progress-*.json | head -1)"
cp "$JSON_SRC" "$JSON_RAW"

echo "→ cifrar con GPG"
# --batch --yes --pinentry-mode loopback: no interactivo en CI
gpg --batch --yes --pinentry-mode loopback --symmetric --cipher-algo AES256 \
  --passphrase "$BACKUP_ENCRYPTION_KEY" \
  -o "$DUMP_ENC" "$DUMP_RAW"
gpg --batch --yes --pinentry-mode loopback --symmetric --cipher-algo AES256 \
  --passphrase "$BACKUP_ENCRYPTION_KEY" \
  -o "$JSON_ENC" "$JSON_RAW"

echo "→ upload R2 s3://${R2_BUCKET}/"
aws s3 cp "$DUMP_ENC" \
  "s3://${R2_BUCKET}/postgres/${DAY}/$(basename "$DUMP_ENC")" \
  --endpoint-url "$ENDPOINT"
aws s3 cp "$JSON_ENC" \
  "s3://${R2_BUCKET}/audit-progress/${DAY}/$(basename "$JSON_ENC")" \
  --endpoint-url "$ENDPOINT"

echo "→ retención: borrar objetos con más de ${RETAIN_DAYS} días"
CUTOFF="$(date -u -d "-${RETAIN_DAYS} days" +%Y%m%d 2>/dev/null || date -u -v-"${RETAIN_DAYS}"d +%Y%m%d)"
for prefix in postgres audit-progress; do
  # Listar "carpetas" día YYYYMMDD bajo el prefijo
  aws s3 ls "s3://${R2_BUCKET}/${prefix}/" --endpoint-url "$ENDPOINT" \
    | awk '{print $2}' | sed 's:/$::' | while read -r daydir; do
      [[ "$daydir" =~ ^[0-9]{8}$ ]] || continue
      if [[ "$daydir" < "$CUTOFF" ]]; then
        echo "  borrando s3://${R2_BUCKET}/${prefix}/${daydir}/"
        aws s3 rm "s3://${R2_BUCKET}/${prefix}/${daydir}/" --recursive --endpoint-url "$ENDPOINT"
      fi
    done
done

echo "OK: backup subido a R2 (postgres/${DAY}/ + audit-progress/${DAY}/)"

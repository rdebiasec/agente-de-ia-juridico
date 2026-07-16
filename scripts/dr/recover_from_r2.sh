#!/usr/bin/env bash
# Descarga y descifra el último paquete de recuperación desde Cloudflare R2.
#
# Requiere:
#   BACKUP_ENCRYPTION_KEY
#   R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
#
# Uso:
#   ./scripts/dr/recover_from_r2.sh                 # prod (default)
#   ./scripts/dr/recover_from_r2.sh --env dev
#   ./scripts/dr/recover_from_r2.sh --env prod --day 20260716
#   ./scripts/dr/recover_from_r2.sh --out ~/Backups/agente-juridico/recovery
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${RECOVERY_OUT:-$HOME/Backups/agente-juridico/recovery}"
DAY=""
ENV_ROOT="${R2_ENV_ROOT:-prod}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="${2:?}"; shift 2 ;;
    --day) DAY="${2:?}"; shift 2 ;;
    --env)
      ENV_ROOT="${2:?}"
      if [[ "$ENV_ROOT" != "prod" && "$ENV_ROOT" != "dev" ]]; then
        echo "ERROR: --env debe ser prod o dev" >&2
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      echo "Uso: recover_from_r2.sh [--env prod|dev] [--day YYYYMMDD] [--out DIR]"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

require() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "ERROR: falta variable de entorno $name" >&2
    exit 1
  fi
}

# Clave desde archivo local (no en git)
if [[ -z "${BACKUP_ENCRYPTION_KEY:-}" && -f "$HOME/Backups/agente-juridico/BACKUP_ENCRYPTION_KEY.txt" ]]; then
  BACKUP_ENCRYPTION_KEY="$(tr -d '\n' <"$HOME/Backups/agente-juridico/BACKUP_ENCRYPTION_KEY.txt")"
  export BACKUP_ENCRYPTION_KEY
fi

# Opcional: R2_* desde .env si no están en el entorno
if [[ -f "$ROOT/.env" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    case "$line" in
      R2_ACCOUNT_ID=*|R2_ACCESS_KEY_ID=*|R2_SECRET_ACCESS_KEY=*|R2_BUCKET=*|BACKUP_ENCRYPTION_KEY=*)
        key="${line%%=*}"
        if [[ -z "${!key:-}" ]]; then
          export "$line"
        fi
        ;;
    esac
  done <"$ROOT/.env"
fi

require BACKUP_ENCRYPTION_KEY
require R2_ACCOUNT_ID
require R2_ACCESS_KEY_ID
require R2_SECRET_ACCESS_KEY
require R2_BUCKET

ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="auto"
export AWS_EC2_METADATA_DISABLED=true

mkdir -p "$OUT"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
WORKDIR="$OUT/run-$STAMP"
mkdir -p "$WORKDIR"

echo "→ entorno R2: ${ENV_ROOT}"
echo "→ leyendo ${ENV_ROOT}/LATEST.txt / día"
if [[ -z "$DAY" ]]; then
  aws s3 cp "s3://${R2_BUCKET}/${ENV_ROOT}/LATEST.txt" "$WORKDIR/LATEST.txt" --endpoint-url "$ENDPOINT"
  DAY="$(grep -E '^created_at_utc=' "$WORKDIR/LATEST.txt" | head -1 | cut -d= -f2 | cut -c1-8 || true)"
  if [[ -z "$DAY" ]]; then
    DAY="$(date -u +%Y%m%d)"
  fi
  echo "  día inferido: $DAY"
  cat "$WORKDIR/LATEST.txt"
else
  echo "  día forzado: $DAY"
fi

echo "→ descargar objetos del día $DAY"
aws s3 sync "s3://${R2_BUCKET}/${ENV_ROOT}/postgres/${DAY}/" "$WORKDIR/postgres/" --endpoint-url "$ENDPOINT"
aws s3 sync "s3://${R2_BUCKET}/${ENV_ROOT}/audit-progress/${DAY}/" "$WORKDIR/audit-progress/" --endpoint-url "$ENDPOINT"
aws s3 sync "s3://${R2_BUCKET}/${ENV_ROOT}/secrets/${DAY}/" "$WORKDIR/secrets/" --endpoint-url "$ENDPOINT"

gpg_dec() {
  local src="$1" dst="$2"
  gpg --batch --yes --pinentry-mode loopback --decrypt \
    --passphrase "$BACKUP_ENCRYPTION_KEY" \
    -o "$dst" "$src"
}

echo "→ descifrar"
DUMP_GPG="$(ls -1t "$WORKDIR"/postgres/*.dump.gpg 2>/dev/null | head -1 || true)"
JSON_GPG="$(ls -1t "$WORKDIR"/audit-progress/*.json.gpg 2>/dev/null | head -1 || true)"
SECRETS_GPG="$(ls -1t "$WORKDIR"/secrets/*.env.gpg 2>/dev/null | head -1 || true)"

if [[ -z "$DUMP_GPG" ]]; then
  echo "ERROR: no hay dump .gpg en postgres/${DAY}/" >&2
  exit 1
fi

DUMP_OUT="$WORKDIR/$(basename "${DUMP_GPG%.gpg}")"
gpg_dec "$DUMP_GPG" "$DUMP_OUT"
echo "  dump → $DUMP_OUT"

if [[ -n "$JSON_GPG" ]]; then
  JSON_OUT="$WORKDIR/$(basename "${JSON_GPG%.gpg}")"
  gpg_dec "$JSON_GPG" "$JSON_OUT"
  echo "  audit JSON → $JSON_OUT"
fi

if [[ -n "$SECRETS_GPG" ]]; then
  SECRETS_OUT="$WORKDIR/secrets.env"
  gpg_dec "$SECRETS_GPG" "$SECRETS_OUT"
  chmod 600 "$SECRETS_OUT"
  # Contar claves sin mostrar valores
  n="$(grep -c '^[A-Z0-9_]\+=' "$SECRETS_OUT" || true)"
  echo "  secrets.env → $SECRETS_OUT ($n variables)"
else
  echo "  AVISO: no hay secrets.env.gpg en este backup"
fi

cat >"$WORKDIR/NEXT_STEPS.txt" <<EOF
Recuperación lista en: $WORKDIR

1) Restaurar Postgres (local):
   ./scripts/dr/restore_postgres.sh "$DUMP_OUT"

2) Restaurar Postgres (producción — PELIGROSO):
   DATABASE_URL='…External…' ./scripts/dr/restore_postgres.sh --remote "$DUMP_OUT"
   (pedirá escribir: RESTORE PRODUCTION)

3) Secretos de la app:
   - Local: copiar claves de secrets.env a .env (no commitear)
   - Render: Dashboard → Environment → pegar SITE_PASSWORD, SESSION_SECRET, OPENAI_API_KEY, etc.

4) Verificar:
   ./scripts/dr/verify_recovery.sh --local
   # o --prod

5) Borrar $WORKDIR cuando termines (contiene secretos en claro).
EOF

echo ""
echo "OK: paquete descifrado en $WORKDIR"
echo "Lea: $WORKDIR/NEXT_STEPS.txt"
cat "$WORKDIR/NEXT_STEPS.txt"

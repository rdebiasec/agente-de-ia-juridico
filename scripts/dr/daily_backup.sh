#!/usr/bin/env bash
# Backup diario: Postgres local (+ prod si PROD_DATABASE_URL) y export JSON de auditoría.
# Uso:
#   ./scripts/dr/daily_backup.sh
#   PROD_DATABASE_URL='postgresql://...' ./scripts/dr/daily_backup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="${BACKUP_LOG_DIR:-$HOME/Backups/agente-juridico/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/daily-backup-$(date +%Y%m%d).log"

exec >>"$LOG" 2>&1
echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) daily_backup start ====="

cd "$ROOT"

echo "→ Postgres local"
"$ROOT/scripts/dr/backup_postgres.sh" --label local || echo "WARN: backup local falló"

if [[ -f "$ROOT/.env" ]]; then
  # shellcheck disable=SC1091
  set -a
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^DATABASE_URL= ]]; then
      export "$line"
    fi
  done < "$ROOT/.env"
  set +a
fi

if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "→ Export audit progress (DATABASE_URL actual)"
  "$ROOT/.venv/bin/python" "$ROOT/scripts/dr/export_audit_progress.py" --label local \
    || echo "WARN: export audit local falló"
fi

if [[ -n "${PROD_DATABASE_URL:-}" ]]; then
  echo "→ Postgres prod"
  DATABASE_URL="$PROD_DATABASE_URL" "$ROOT/scripts/dr/backup_postgres.sh" --label prod \
    || echo "WARN: backup prod falló"
  echo "→ Export audit progress prod"
  DATABASE_URL="$PROD_DATABASE_URL" \
    "$ROOT/.venv/bin/python" "$ROOT/scripts/dr/export_audit_progress.py" --label prod \
    || echo "WARN: export audit prod falló"
else
  echo "INFO: PROD_DATABASE_URL no definida — omitiendo backup de producción."
  echo "      Configure en el entorno del launchd/cron (External Database URL de Render)."
fi

# Retener dumps > 30 días (solo archivos, no el directorio)
find "$HOME/Backups/agente-juridico/postgres" -type f -name 'agente-*.dump' -mtime +30 -delete 2>/dev/null || true
find "$HOME/Backups/agente-juridico/audit-progress" -type f -name 'audit-progress-*.json' -mtime +60 -delete 2>/dev/null || true

echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) daily_backup done ====="

#!/usr/bin/env bash
# Inventario de variables .env vs .env.example (nunca imprime valores).
# Compatible con bash 3.2 (macOS). Uso: ./scripts/dr/env_inventory.sh [--save]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXAMPLE="$ROOT/.env.example"
ENV_FILE="$ROOT/.env"
SAVE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --save) SAVE=1; shift ;;
    -h|--help)
      echo "Uso: env_inventory.sh [--save]"
      echo "  Lista claves de .env.example: SET | EMPTY | MISSING"
      echo "  --save escribe reporte en ~/Backups/agente-juridico/ (sin valores)."
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$EXAMPLE" ]]; then
  echo "ERROR: no existe $EXAMPLE" >&2
  exit 1
fi

lookup_env_status() {
  local key="$1"
  local line val
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "MISSING"
    return
  fi
  line="$(grep -E "^[[:space:]]*${key}=" "$ENV_FILE" | tail -1 || true)"
  if [[ -z "$line" ]]; then
    echo "MISSING"
    return
  fi
  val="${line#*=}"
  val="${val%\"}"
  val="${val#\"}"
  val="${val%\'}"
  val="${val#\'}"
  if [[ -z "$val" ]]; then
    echo "EMPTY"
  else
    echo "SET"
  fi
}

if [[ ! -f "$ENV_FILE" ]]; then
  echo "AVISO: no existe .env (todas las claves aparecerán como MISSING)."
fi

TMP_KEYS="$(mktemp)"
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  case "$line" in
    *=*) ;;
    *) continue ;;
  esac
  key="${line%%=*}"
  # trim spaces
  key="$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -n "$key" ]] && echo "$key"
done < "$EXAMPLE" | awk '!seen[$0]++' >"$TMP_KEYS"

REPORT="$(mktemp)"
{
  echo "# Inventario env — $(date '+%Y-%m-%d %H:%M')"
  echo "# Fuente de claves: .env.example — nunca incluye valores"
  echo ""
  echo "| Variable | Estado |"
  echo "|----------|--------|"
} >"$REPORT"

set_count=0
empty_count=0
missing_count=0

while IFS= read -r k || [[ -n "$k" ]]; do
  [[ -z "$k" ]] && continue
  status="$(lookup_env_status "$k")"
  case "$status" in
    SET) set_count=$((set_count + 1)) ;;
    EMPTY) empty_count=$((empty_count + 1)) ;;
    MISSING) missing_count=$((missing_count + 1)) ;;
  esac
  echo "| \`$k\` | $status |" >>"$REPORT"
done <"$TMP_KEYS"

{
  echo ""
  echo "Resumen: SET=$set_count EMPTY=$empty_count MISSING=$missing_count"
} >>"$REPORT"

cat "$REPORT"
rm -f "$TMP_KEYS"

if [[ "$SAVE" -eq 1 ]]; then
  OUTDIR="${BACKUP_DIR:-$HOME/Backups/agente-juridico}"
  mkdir -p "$OUTDIR"
  OUT="$OUTDIR/env-inventory-$(date +%Y%m%d-%H%M).txt"
  cp "$REPORT" "$OUT"
  echo ""
  echo "OK: guardado en $OUT"
fi
rm -f "$REPORT"

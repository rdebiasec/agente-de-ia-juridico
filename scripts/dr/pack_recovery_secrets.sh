#!/usr/bin/env bash
# Empaqueta variables de recuperación en un .env plano (sin imprimir valores).
# Lee del entorno las claves listadas; omite vacías.
#
# Uso:
#   ./scripts/dr/pack_recovery_secrets.sh /tmp/secrets.env
set -euo pipefail

OUT="${1:?indique archivo de salida}"

# Claves que permiten reconstruir Render / local tras un desastre.
# No incluir BACKUP_ENCRYPTION_KEY (vive fuera, en gestor de contraseñas).
KEYS=(
  SITE_USERNAME
  SITE_PASSWORD
  SESSION_SECRET
  SESSION_IDLE_MINUTES
  SESSION_MAX_MESSAGES
  SESSION_COOKIE_SECURE
  AGENT_MAX_TURNS
  DEV_AUTO_LOGIN
  OPENAI_API_KEY
  OPENAI_MODEL
  EMBEDDING_MODEL
  PROD_DATABASE_URL
  DATABASE_URL
  SLACK_BOT_TOKEN
  SLACK_SIGNING_SECRET
  SLACK_REVIEW_CHANNEL
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_MESSAGING_SERVICE_SID
  TWILIO_FROM_NUMBER
  TWILIO_ALERT_TO
  TWILIO_STATUS_CALLBACK
  AUDIT_CORS_ORIGINS
)

: >"$OUT"
count=0
for key in "${KEYS[@]}"; do
  val="${!key:-}"
  if [[ -z "$val" ]]; then
    continue
  fi
  # Escapar valores con saltos de línea no esperados
  printf '%s=%s\n' "$key" "$val" >>"$OUT"
  count=$((count + 1))
done

if [[ "$count" -eq 0 ]]; then
  echo "ERROR: ninguna variable de recuperación presente en el entorno." >&2
  exit 1
fi

echo "→ secrets.env: $count variables (valores no mostrados)"

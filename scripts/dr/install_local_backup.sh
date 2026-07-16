#!/usr/bin/env bash
# Instala backup LOCAL automático (Postgres + auditoría + secrets → R2).
# - Escribe ~/Backups/agente-juridico/backup.env (chmod 600)
# - LaunchAgent: al cargar sesión + cada 6 h (sólido si la Mac duerme a las 02:30)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_ROOT="$HOME/Backups/agente-juridico"
CONF="$BACKUP_ROOT/backup.env"
PLIST_DIR="$HOME/Library/LaunchAgents"
LABEL="com.dbx.agente-juridico.local-backup"
PLIST="$PLIST_DIR/${LABEL}.plist"
SCRIPT="$ROOT/scripts/dr/backup_local_to_r2.sh"
WRAPPER="$BACKUP_ROOT/bin/run_local_backup.sh"

mkdir -p "$BACKUP_ROOT/logs" "$BACKUP_ROOT/bin" "$PLIST_DIR"
chmod +x "$SCRIPT" "$ROOT/scripts/dr/pack_recovery_secrets.sh" "$ROOT/scripts/dr/export_audit_progress.py"

# Wrapper fuera de Documents (evita bloqueos TCC de launchd en macOS)
cat >"$WRAPPER" <<EOF
#!/bin/bash
exec /bin/bash $(printf '%q' "$SCRIPT")
EOF
chmod +x "$WRAPPER"

# --- Credenciales R2 / GPG ---
# Prioridad: env ya exportado → backup.env existente → BACKUP_ENCRYPTION_KEY.txt + vars R2_*
ENC_KEY="${BACKUP_ENCRYPTION_KEY:-}"
if [[ -z "$ENC_KEY" && -f "$BACKUP_ROOT/BACKUP_ENCRYPTION_KEY.txt" ]]; then
  ENC_KEY="$(tr -d '\n' <"$BACKUP_ROOT/BACKUP_ENCRYPTION_KEY.txt")"
fi
if [[ -z "$ENC_KEY" && -f "$CONF" ]]; then
  # shellcheck disable=SC1090
  ENC_KEY="$(set -a; source "$CONF"; set +a; echo "${BACKUP_ENCRYPTION_KEY:-}")"
fi

R2_ACCOUNT_ID="${R2_ACCOUNT_ID:-}"
R2_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID:-}"
R2_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY:-}"
R2_BUCKET="${R2_BUCKET:-agente-ia-juridico-backups}"

if [[ -f "$CONF" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$CONF"; set +a
  R2_ACCOUNT_ID="${R2_ACCOUNT_ID:-}"
  R2_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID:-}"
  R2_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY:-}"
  R2_BUCKET="${R2_BUCKET:-agente-ia-juridico-backups}"
  ENC_KEY="${BACKUP_ENCRYPTION_KEY:-$ENC_KEY}"
fi

missing=0
for v in ENC_KEY R2_ACCOUNT_ID R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY R2_BUCKET; do
  if [[ -z "${!v:-}" ]]; then
    echo "ERROR: falta $v para escribir $CONF" >&2
    missing=1
  fi
done
if [[ "$missing" -eq 1 ]]; then
  cat >&2 <<'EOF'
Pase las variables al instalar, por ejemplo:

  BACKUP_ENCRYPTION_KEY='…' \
  R2_ACCOUNT_ID='…' R2_ACCESS_KEY_ID='…' R2_SECRET_ACCESS_KEY='…' \
  R2_BUCKET='agente-ia-juridico-backups' \
  ./scripts/dr/install_local_backup.sh

O cree antes ~/Backups/agente-juridico/BACKUP_ENCRYPTION_KEY.txt
EOF
  exit 1
fi

umask 077
cat >"$CONF" <<EOF
# Generado por install_local_backup.sh — NO commitear
BACKUP_ENCRYPTION_KEY=${ENC_KEY}
R2_ACCOUNT_ID=${R2_ACCOUNT_ID}
R2_ACCESS_KEY_ID=${R2_ACCESS_KEY_ID}
R2_SECRET_ACCESS_KEY=${R2_SECRET_ACCESS_KEY}
R2_BUCKET=${R2_BUCKET}
EOF
chmod 600 "$CONF"
echo "OK: $CONF (chmod 600)"

# Asegurar awscli en venv
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  "$ROOT/.venv/bin/python" -m pip install -q "awscli>=1.32,<2" || true
fi

# LaunchAgent: RunAtLoad + cada 6 horas (mejor disponibilidad que solo 02:30)
cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${WRAPPER}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>21600</integer>
  <key>Nice</key>
  <integer>10</integer>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key>
    <string>${HOME}</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${BACKUP_ROOT}/logs/launchd-local-stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${BACKUP_ROOT}/logs/launchd-local-stderr.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true
# Disparo inmediato (además de RunAtLoad)
launchctl kickstart -k "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "OK: LaunchAgent ${LABEL}"
echo "  Frecuencia: al iniciar sesión + cada 6 horas (si la Mac está despierta)"
echo "  Destino: R2 s3://${R2_BUCKET}/local/… + ~/Backups/agente-juridico/"
echo "  Logs: ${BACKUP_ROOT}/logs/"
echo "Estado: launchctl print gui/\$(id -u)/${LABEL} | head"
echo "Prueba en primer plano: $SCRIPT"

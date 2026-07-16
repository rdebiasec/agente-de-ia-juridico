#!/usr/bin/env bash
# Instala LaunchAgent macOS para backup diario a las 02:30.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST="$PLIST_DIR/com.dbx.agente-juridico.daily-backup.plist"
LABEL="com.dbx.agente-juridico.daily-backup"

mkdir -p "$PLIST_DIR" "$HOME/Backups/agente-juridico/logs"

# PROD_DATABASE_URL: opcional, External URL de Render (nunca commitear).
PROD_URL="${PROD_DATABASE_URL:-}"

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
    <string>${ROOT}/scripts/dr/daily_backup.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>2</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
    <key>PROD_DATABASE_URL</key>
    <string>${PROD_URL}</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${HOME}/Backups/agente-juridico/logs/launchd-stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${HOME}/Backups/agente-juridico/logs/launchd-stderr.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "OK: LaunchAgent instalado → $PLIST"
echo "Backup diario a las 02:30. Logs: ~/Backups/agente-juridico/logs/"
if [[ -z "$PROD_URL" ]]; then
  echo "AVISO: instale de nuevo con PROD_DATABASE_URL='postgresql://…' para incluir producción."
fi
echo "Prueba ahora: ./scripts/dr/daily_backup.sh"

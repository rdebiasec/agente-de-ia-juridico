#!/usr/bin/env bash
# Validación extensa del sistema — capas 1→5 (solo local).
# Uso: ./scripts/validacion_sistema_completa.sh
# Salida: docs/auditoria/validacion-sistema-completa-reporte.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/.venv/bin/python"
PYTEST="${ROOT}/.venv/bin/pytest"
REPORT="${ROOT}/docs/auditoria/validacion-sistema-completa-reporte.md"
SERVER_PID=""
STARTED_SERVER=0

# shellcheck disable=SC1091
LOAD_DOTENV_PYTHON="${ROOT}/.venv/bin/python"
# shellcheck source=scripts/lib/load_dotenv.sh
source "${ROOT}/scripts/lib/load_dotenv.sh"
load_dotenv "${ROOT}/.env"
# Credenciales de smoke (plaintext) si existen — no van a git.
if [[ -f "${HOME}/Backups/agente-juridico/smoke.env" ]]; then
  load_dotenv "${HOME}/Backups/agente-juridico/smoke.env"
fi

log() { printf '%s\n' "$*"; }

# Tests y smoke local usan memoria si Postgres no responde.
if [[ -n "${DATABASE_URL:-}" ]]; then
  if ! "$PY" -c "
import os, sys
url = os.environ.get('DATABASE_URL', '')
try:
    from sqlalchemy import create_engine, text
    e = create_engine(url, pool_pre_ping=True)
    with e.connect() as c:
        c.execute(text('SELECT 1'))
except Exception:
    sys.exit(1)
" 2>/dev/null; then
    log "Postgres no disponible — validación en modo memoria."
    export DATABASE_URL=""
  fi
else
  export DATABASE_URL=""
fi

# Capa 5 usa puerto dedicado para no pelear con el servidor de desarrollo
# y para poder fijar SITE_PASSWORD en claro (el .env suele tener hash PBKDF2).
export SMOKE_BASE_URL="${SMOKE_BASE_URL:-http://127.0.0.1:8010}"
export SMOKE_SITE_PASSWORD="${SMOKE_SITE_PASSWORD:-test-secret-pass-long}"
export SMOKE_SITE_USERNAME="${SMOKE_SITE_USERNAME:-${SITE_USERNAME:-despacho}}"
export SMOKE_AUDIT_EMAIL="${SMOKE_AUDIT_EMAIL:-smoke@despacho.com}"
export SMOKE_AUDIT_PIN="${SMOKE_AUDIT_PIN:-654321}"

declare -a LAYER_NAMES=()
declare -a LAYER_STATUS=()
declare -a LAYER_DETAIL=()
declare -a LAYER_SECONDS=()

cleanup() {
  if [[ "$STARTED_SERVER" -eq 1 ]] && [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

run_layer() {
  local name="$1"
  shift
  local t0 t1 elapsed rc out
  log ""
  log "=== $name ==="
  t0=$(date +%s)
  set +e
  out="$("$@" 2>&1)"
  rc=$?
  set -e
  t1=$(date +%s)
  elapsed=$((t1 - t0))
  LAYER_NAMES+=("$name")
  LAYER_SECONDS+=("$elapsed")
  if [[ $rc -eq 0 ]]; then
    LAYER_STATUS+=("OK")
    LAYER_DETAIL+=("$(echo "$out" | tail -n 8)")
    log "OK (${elapsed}s)"
  else
    LAYER_STATUS+=("FAIL")
    LAYER_DETAIL+=("$(echo "$out" | tail -n 25)")
    log "FAIL (${elapsed}s)"
    echo "$out" >&2
    write_report
    exit "$rc"
  fi
}

wait_for_health() {
  local i
  for i in $(seq 1 60); do
    if curl -sf "${SMOKE_BASE_URL}/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_server() {
  if curl -sf "${SMOKE_BASE_URL}/health" >/dev/null 2>&1; then
    log "Servidor smoke ya activo en ${SMOKE_BASE_URL}"
    return 0
  fi
  local smoke_port
  smoke_port="$(printf '%s' "${SMOKE_BASE_URL}" | sed -E 's#.*:([0-9]+).*#\1#')"
  smoke_port="${smoke_port:-8010}"
  if lsof -ti ":${smoke_port}" >/dev/null 2>&1; then
    lsof -ti ":${smoke_port}" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
  log "→ Generando portal auditoría..."
  AUDIT_API_BASE="" "$PY" scripts/generar_audit_portal.py >/dev/null
  log "→ Arrancando servidor smoke en :${smoke_port} (SITE_PASSWORD=SMOKE_SITE_PASSWORD)..."
  # Plaintext para que test_smoke_local pueda hacer login; no usa el hash del .env.
  PORT="${smoke_port}" \
    SITE_PASSWORD="${SMOKE_SITE_PASSWORD}" \
    DEV_AUTO_LOGIN=false \
    SESSION_COOKIE_SECURE=false \
    "$PY" -m src.main >/tmp/agente-smoke-server.log 2>&1 &
  SERVER_PID=$!
  STARTED_SERVER=1
  wait_for_health
}


write_report() {
  local now verdicts skills_ok failed=0 i
  now=$(date "+%Y-%m-%d %H:%M")
  mkdir -p "$(dirname "$REPORT")"

  skills_ok="—"
  if [[ -f "${ROOT}/docs/auditoria/validacion-7-expertos-data.json" ]]; then
    skills_ok=$("$PY" -c "
import json
from pathlib import Path
from collections import Counter
d = json.loads(Path('docs/auditoria/validacion-7-expertos-data.json').read_text())
print(dict(Counter(s['veredicto'] for s in d['skills'].values())))
" 2>/dev/null || echo "—")
  fi

  for i in "${!LAYER_NAMES[@]}"; do
    if [[ "${LAYER_STATUS[$i]}" != "OK" ]]; then
      failed=$((failed + 1))
    fi
  done

  {
    echo "# Reporte — Validación extensa del sistema (${now})"
    echo ""
    echo "## Resumen ejecutivo"
    echo ""
    if [[ $failed -eq 0 ]]; then
      echo "**Resultado global: PASS** — todas las capas completadas."
    else
      echo "**Resultado global: FAIL** — ${failed} capa(s) con error."
    fi
    echo ""
    echo "| Capa | Estado | Duración (s) |"
    echo "|------|--------|-------------:|"
    for i in "${!LAYER_NAMES[@]}"; do
      echo "| ${LAYER_NAMES[$i]} | ${LAYER_STATUS[$i]} | ${LAYER_SECONDS[$i]} |"
    done
    echo ""
    echo "### Skills 7-expertos (Capa 1)"
    echo ""
    echo "Veredictos: \`${skills_ok}\`"
    echo "Detalle: [validacion-7-expertos-reporte.md](validacion-7-expertos-reporte.md)"
    echo ""
    echo "## Reglas de negocio verificadas"
    echo ""
    echo "| Regla | Verificación |"
    echo "|-------|--------------|"
    echo "| Tutela solo tras evaluador | Cadenas + test_sistema_runtime |"
    echo "| Ruta 906 no redacta recursos | SKILL.md + cadenas |"
    echo "| HITL cliente / salidas | compliance + smoke audit |"
    echo "| IA propone; abogado aprueba | guardrails skills + HITL tests |"
    echo ""
    echo "## Riesgos residuales"
    echo ""
    echo "1. LLM real no probado en esta validación (routing determinista)."
    echo "2. Slack sin token en entorno local."
    echo "3. REQ-001…050 sin checklist formal automatizado."
    echo "4. Smoke solo local (sin producción Render)."
    echo "5. 10 skills mono-agente sin sección Rol en (aceptable si atómicos)."
    echo ""
    echo "## Repetir validación"
    echo ""
    echo '```bash'
    echo "./scripts/validacion_sistema_completa.sh"
    echo '```'
    echo ""
    echo "## Detalle por capa"
    echo ""
    for i in "${!LAYER_NAMES[@]}"; do
      echo "### ${LAYER_NAMES[$i]}"
      echo '```'
      echo "${LAYER_DETAIL[$i]}"
      echo '```'
      echo ""
    done
  } >"$REPORT"
  log "Reporte: $REPORT"
}

# --- Capa 1 ---
run_layer "Capa 1 — Skills 7-expertos" "$PY" scripts/validar_skills_metricas.py

# --- Capa 2 ---
run_layer "Capa 2 — Gates estáticos" "$PY" -c "
import subprocess, sys
from pathlib import Path
root = Path('${ROOT}')
py = '${PY}'
steps = [
    [py, 'scripts/validate_fase0.py'],
    [py, 'scripts/auditar_pasos_skills_gerencia.py', '--check'],
]
import os
os.environ['AUDIT_API_BASE'] = ''
steps.append([py, 'scripts/generar_audit_portal.py'])
for cmd in steps:
    r = subprocess.run(cmd, cwd=root)
    if r.returncode:
        sys.exit(r.returncode)
missing = 0
for skill in (root / '.cursor/skills').glob('*/SKILL.md'):
    sid = skill.parent.name
    mirror = root / 'agente/skills' / sid / 'SKILL.md'
    if not mirror.is_file() or mirror.read_text() != skill.read_text():
        print(f'Espejo desincronizado: {sid}')
        missing += 1
if missing:
    print(f'{missing} skills desincronizados')
    sys.exit(1)
print('Espejo OK: 90 SKILL.md sincronizados')
"

# --- Capa 3 ---
run_layer "Capa 3 — Pytest suite" "$PYTEST" tests/ -q --tb=line -m "not smoke"

# --- Capa 4 ---
run_layer "Capa 4 — Runtime" "$PYTEST" tests/test_sistema_runtime.py -q

# --- Capa 5 ---
log ""
log "=== Capa 5 — Smoke HTTP local ==="
t0=$(date +%s)
set +e
start_server
smoke_out=$("$PYTEST" tests/test_smoke_local.py -v --tb=short -m smoke 2>&1)
smoke_rc=$?
set -e
t1=$(date +%s)
LAYER_NAMES+=("Capa 5 — Smoke HTTP local")
LAYER_SECONDS+=("$((t1 - t0))")
if [[ $smoke_rc -eq 0 ]]; then
  LAYER_STATUS+=("OK")
  LAYER_DETAIL+=("$(echo "$smoke_out" | tail -n 8)")
  log "OK ($((t1 - t0))s)"
else
  LAYER_STATUS+=("FAIL")
  LAYER_DETAIL+=("$(echo "$smoke_out" | tail -n 25)")
  log "FAIL ($((t1 - t0))s)"
  echo "$smoke_out" >&2
  write_report
  exit "$smoke_rc"
fi

write_report
log ""
log "Validación extensa completada."

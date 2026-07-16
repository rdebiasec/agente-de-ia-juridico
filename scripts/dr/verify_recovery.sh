#!/usr/bin/env bash
# Verificación post-recuperación (local y/o prod).
# Uso:
#   ./scripts/dr/verify_recovery.sh --local
#   ./scripts/dr/verify_recovery.sh --prod
#   ./scripts/dr/verify_recovery.sh --local --prod
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
DO_LOCAL=0
DO_PROD=0
FAIL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local) DO_LOCAL=1; shift ;;
    --prod) DO_PROD=1; shift ;;
    -h|--help)
      echo "Uso: verify_recovery.sh --local|--prod [--local --prod]"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
done

if [[ "$DO_LOCAL" -eq 0 && "$DO_PROD" -eq 0 ]]; then
  echo "Indique --local y/o --prod." >&2
  exit 1
fi

check_pass() {
  local name="$1" ok="$2" detail="$3"
  if [[ "$ok" == "1" ]]; then
    echo "  PASS  $name — $detail"
  else
    echo "  FAIL  $name — $detail"
    FAIL=$((FAIL + 1))
  fi
}

if [[ "$DO_LOCAL" -eq 1 ]]; then
  echo "=== Verificación LOCAL ==="
  HEALTH_URL="${LOCAL_URL:-http://127.0.0.1:8000}/health"
  if health_json="$(curl -sf --max-time 5 "$HEALTH_URL" 2>/dev/null)"; then
    persist="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('persistencia','?'))" 2>/dev/null || echo "?")"
    envn="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('environment','?'))" 2>/dev/null || echo "?")"
    status="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "?")"
    [[ "$status" == "ok" ]] && ok=1 || ok=0
    check_pass "/health status" "$ok" "status=$status env=$envn persistencia=$persist"
    [[ "$persist" == "postgres" ]] && ok=1 || ok=0
    check_pass "persistencia postgres" "$ok" "$persist"
  else
    check_pass "/health alcanzable" "0" "no responde en $HEALTH_URL (¿start-local.sh?)"
  fi

  aud_code="$(curl -sf -o /dev/null -w '%{http_code}' --max-time 5 "${LOCAL_URL:-http://127.0.0.1:8000}/auditoria/" 2>/dev/null || echo "000")"
  [[ "$aud_code" == "200" ]] && ok=1 || ok=0
  check_pass "/auditoria/" "$ok" "HTTP $aud_code"

  echo "→ pytest mínimo (auth/security)..."
  if "$ROOT/.venv/bin/python" -m pytest \
    tests/test_auth.py tests/test_security.py tests/test_prod_followups.py -q --tb=no; then
    check_pass "pytest auth/security" "1" "ok"
  else
    check_pass "pytest auth/security" "0" "fallaron tests"
  fi
  echo ""
fi

if [[ "$DO_PROD" -eq 1 ]]; then
  echo "=== Verificación PRODUCCIÓN ==="
  RENDER="${RENDER_URL:-https://agente-de-ia-juridico.onrender.com}"
  if health_json="$(curl -sf --max-time 60 "$RENDER/health" 2>/dev/null)"; then
    persist="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('persistencia','?'))" 2>/dev/null || echo "?")"
    envn="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('environment','?'))" 2>/dev/null || echo "?")"
    auth="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('web_auth_enabled','?'))" 2>/dev/null || echo "?")"
    auto="$(echo "$health_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('dev_auto_login','?'))" 2>/dev/null || echo "?")"
    [[ "$persist" == "postgres" ]] && ok=1 || ok=0
    check_pass "prod persistencia" "$ok" "$persist"
    [[ "$auth" == "True" || "$auth" == "true" ]] && ok=1 || ok=0
    check_pass "web_auth_enabled" "$ok" "$auth"
    [[ "$auto" == "False" || "$auto" == "false" ]] && ok=1 || ok=0
    check_pass "dev_auto_login false" "$ok" "$auto (env=$envn)"
  else
    check_pass "prod /health" "0" "no responde (cold start / caída)"
  fi

  echo "→ smoke_produccion.sh..."
  REPORT="$ROOT/docs/auditoria/smoke-produccion-reporte.md"
  if "$ROOT/scripts/smoke_produccion.sh" "$REPORT"; then
    check_pass "smoke_produccion" "1" "PASS"
  else
    check_pass "smoke_produccion" "0" "ver $REPORT"
  fi
  echo ""
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "Resultado: PASS"
  exit 0
fi
echo "Resultado: FAIL ($FAIL checks)"
exit 1

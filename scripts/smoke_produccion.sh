#!/usr/bin/env bash
# Smoke producción — Render + GitHub Pages (sin credenciales).
set -euo pipefail

RENDER="${RENDER_URL:-https://agente-de-ia-juridico.onrender.com}"
PAGES="${PAGES_URL:-https://rdebiasec.github.io/agente-de-ia-juridico}"
REPORT="${1:-docs/auditoria/smoke-produccion-reporte.md}"

mkdir -p "$(dirname "$REPORT")"
now=$(date "+%Y-%m-%d %H:%M")
fail=0

check() {
  local name="$1"
  local ok="$2"
  local detail="$3"
  if [[ "$ok" == "1" ]]; then
    echo "| $name | PASS | $detail |"
  else
    echo "| $name | FAIL | $detail |"
    fail=$((fail + 1))
  fi
}

render_guardrails=$(curl -sf "$RENDER/api/audit/catalog" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d.get('guardrails',[])))" 2>/dev/null || echo 0)
render_skills=$(curl -sf "$RENDER/api/audit/catalog" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d.get('skills',[])))" 2>/dev/null || echo 0)
pages_guardrails=$(curl -sfL "$PAGES/audit-data.json" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d.get('guardrails',[])))" 2>/dev/null || echo 0)
pages_skills=$(curl -sfL "$PAGES/audit-data.json" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d.get('skills',[])))" 2>/dev/null || echo 0)
csp=$(curl -sI "$RENDER/auditoria/" | grep -i content-security-policy || true)
health=$(curl -sf "$RENDER/health" | python3 -c "import sys,json;h=json.load(sys.stdin);print(h.get('persistencia','?'),h.get('environment','?'),h.get('web_auth_enabled','?'))" 2>/dev/null || echo "error")
cors=$(curl -sI -X OPTIONS "$RENDER/api/audit/catalog" -H "Origin: https://rdebiasec.github.io" -H "Access-Control-Request-Method: GET" | grep -i access-control-allow-origin || true)
ui_text=$(curl -sfL "$RENDER/auditoria/index.html" | grep -c "10 reglas estrictas" || echo 0)
api_base=$(curl -sfL "$PAGES/audit-api-config.js" | grep -o 'https://[^"]*' | head -1 || echo "")

{
  echo "# Smoke producción — $now"
  echo ""
  echo "**Render:** $RENDER"
  echo "**Pages:** $PAGES"
  echo ""
  echo "| Check | Estado | Detalle |"
  echo "|-------|--------|---------|"
  [[ "$render_guardrails" == "10" ]] && rg_ok=1 || rg_ok=0
  check "Render catálogo guardrails" "$rg_ok" "$render_guardrails (esperado 10)"
  [[ "$render_skills" == "90" ]] && rs_ok=1 || rs_ok=0
  check "Render catálogo skills" "$rs_ok" "$render_skills (esperado 90)"
  [[ "$pages_guardrails" == "10" ]] && pg_ok=1 || pg_ok=0
  check "Pages audit-data guardrails" "$pg_ok" "$pages_guardrails"
  [[ "$pages_skills" == "90" ]] && ps_ok=1 || ps_ok=0
  check "Pages audit-data skills" "$ps_ok" "$pages_skills"
  echo "$csp" | grep -q tailwindcss && csp_ok=1 || csp_ok=0
  check "CSP Tailwind en /auditoria/" "$csp_ok" "$(echo "$csp" | tr -d '\r' | head -c 120)"
  echo "$cors" | grep -qi github.io && cors_ok=1 || cors_ok=0
  check "CORS Pages → Render" "$cors_ok" "$(echo "$cors" | tr -d '\r')"
  [[ "$ui_text" -ge 1 ]] && ui_ok=1 || ui_ok=0
  check "UI «10 reglas estrictas»" "$ui_ok" "coincidencias=$ui_text"
  echo "$api_base" | grep -q onrender.com && ab_ok=1 || ab_ok=0
  check "Pages AUDIT_API_BASE → Render" "$ab_ok" "$api_base"
  echo "| /health Render | INFO | $health |"
  echo ""
  if [[ $fail -eq 0 ]]; then
    echo "**Resultado: PASS** ($fail fallos)"
  else
    echo "**Resultado: FAIL** ($fail fallos)"
  fi
} >"$REPORT"

cat "$REPORT"
exit "$fail"

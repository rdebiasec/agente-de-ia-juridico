# Smoke producción — 2026-08-04 15:05

**Render:** https://agente-de-ia-juridico.onrender.com
**Pages:** https://rdebiasec.github.io/agente-de-ia-juridico

| Check | Estado | Detalle |
|-------|--------|---------|
| Render catálogo guardrails | PASS | 10 (esperado 10) |
| Render catálogo skills | PASS | 90 (esperado 90) |
| Pages audit-data guardrails | PASS | 10 |
| Pages audit-data skills | FAIL | 81 |
| CSP Tailwind en /auditoria/ | PASS | content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 's |
| CORS Pages → Render | PASS | access-control-allow-origin: https://rdebiasec.github.io |
| UI editor por agente (tab Guardrails) | PASS | coincidencias=2 |
| Pages AUDIT_API_BASE → Render | PASS | https://agente-de-ia-juridico.onrender.com |
| /health Render | INFO | postgres production False |

**Resultado: FAIL** (1 fallos)

# Smoke producción — 2026-07-16 00:09

**Render:** https://agente-de-ia-juridico.onrender.com  
**Pages:** https://rdebiasec.github.io/agente-de-ia-juridico  
**Commit live:** `d451c92`

| Check | Estado | Detalle |
|-------|--------|---------|
| Render catálogo guardrails | PASS | 10 (esperado 10) |
| Render catálogo skills | PASS | 90 (esperado 90) |
| Pages audit-data guardrails | PASS | 10 |
| Pages audit-data skills | PASS | 90 |
| CSP Tailwind en /auditoria/ | PASS | content-security-policy con Tailwind CDN |
| CORS Pages → Render | PASS | access-control-allow-origin: https://rdebiasec.github.io |
| UI «10 reglas estrictas» | PASS | coincidencias=3 |
| Pages AUDIT_API_BASE → Render | PASS | https://agente-de-ia-juridico.onrender.com |
| /health Render | INFO | postgres production True |
| Login audit prod (prelogin+PIN+session+logout) | PASS | `scripts/smoke_audit_login.py --prod` |
| OpenAPI `/docs` prod | PASS | HTTP 404 (oculto en Render) |

**Resultado: PASS** (0 fallos)

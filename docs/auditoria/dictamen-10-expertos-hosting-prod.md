# Dictamen 10 expertos — hosting seguro y reputación (producción)

**Fecha:** 2026-07-16T05:36:29.351693+00:00
**Commit:** `af2ad58`
**Target:** https://agente-de-ia-juridico.onrender.com
**Pages:** https://rdebiasec.github.io/agente-de-ia-juridico
**Veredicto:** **GO** — PASS=31 WARN=0 FAIL=0 INFO=2

## Panel

| ID | Experto | Resultado | Notas |
|----|---------|-----------|-------|
| E01 | AppSec (OWASP) | PASS | todos PASS |
| E02 | Platform / hosting | PASS | todos PASS |
| E03 | Identity & access | PASS | todos PASS |
| E04 | Data protection / privacy | PASS | todos PASS |
| E05 | Backup & disaster recovery | PASS | todos PASS |
| E06 | Secrets management | PASS | todos PASS |
| E07 | Availability & reliability | PASS | E07-03:INFO |
| E08 | Reputation / legal-tech trust | PASS | todos PASS |
| E09 | Supply chain / CI-CD | PASS | E09-02:INFO |
| E10 | Boundary / CORS / abuse | PASS | todos PASS |

## Hallazgos

| Experto | Test | Estado | Detalle | Fuente |
|---------|------|--------|---------|--------|
| E01 | E01-01 CSP en /auditoria/ | PASS | default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self | https://owasp.org/www-project-secure-headers/ |
| E01 | E01-02 HSTS | PASS | max-age=31536000; includeSubDomains | https://owasp.org/www-project-secure-headers/ |
| E01 | E01-03 X-Frame-Options | PASS | DENY | https://owasp.org/www-project-secure-headers/ |
| E01 | E01-04 OpenAPI oculto en prod | PASS | docs=404 openapi=404 | https://owasp.org/www-project-application-security-verification-standard/ |
| E02 | E02-01 Health production + postgres | PASS | {'status': 'ok', 'environment': 'production', 'persistencia': 'postgres', 'openai_configured': True} | https://render.com/docs |
| E02 | E02-02 DEV_AUTO_LOGIN off | PASS | dev_auto_login=False | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E02 | E02-03 HTTPS servicio alcanzable | PASS | https_health=200 http_probe=200 | https://owasp.org/www-project-application-security-verification-standard/ |
| E03 | E03-01 Prelogin exige password | PASS | HTTP 422 | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E03 | E03-02 Bad password → 401 | PASS | HTTP 401 | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E03 | E03-03 Progress sin sesión → 401 | PASS | HTTP 401 | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E03 | E03-04 Chat sin sesión → 401 | PASS | HTTP 401 | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E04 | E04-01 Aviso privacidad publicado | PASS | HTTP 200 | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981 |
| E04 | E04-02 Tratamiento datos de casos | PASS | HTTP 200 | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981 |
| E04 | E04-03 Policy API + contacto ARCO | PASS | contact=privacidad@dbxsolutions.com | https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581 |
| E05 | E05-01 Workflow backup Postgres→R2 | PASS | .github/workflows/backup-postgres.yml | https://render.com/docs/postgresql-backups |
| E05 | E05-02 Plan de desastre documentado | PASS | PLAN_DESASTRE.md | https://csrc.nist.gov/pubs/sp/800/34/r1/final |
| E05 | E05-03 Último backup Actions success | PASS | [{"conclusion": "success", "createdAt": "2026-07-16T04:15:33Z", "displayTitle": "Backup Postgres → R2"}] | https://render.com/docs/postgresql-backups |
| E06 | E06-01 .env no trackeado en git | PASS | tracked=none | https://owasp.org/www-project-application-security-verification-standard/ |
| E06 | E06-02 Auth web habilitada en prod | PASS | web_auth_enabled=True | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E06 | E06-03 Herramienta hash SITE_PASSWORD | PASS | hash_site_password.py | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html |
| E07 | E07-01 Health latency x3 < 15s | PASS | ms=[230, 216, 210] | https://render.com/docs |
| E07 | E07-02 OpenAI configurado | PASS | openai=True | ops |
| E07 | E07-03 Slack HITL canal | INFO | slack=False | ops |
| E08 | E08-01 Chat abogado alcanzable | PASS | HTTP 200 | producto |
| E08 | E08-02 Anti-wipe merge en portal | PASS | merge=True | integridad de datos |
| E08 | E08-03 Logout no borra cache local | PASS | wipe_helpers=False | integridad de datos |
| E09 | E09-01 CI workflow presente | PASS | ci.yml | https://owasp.org/www-project-application-security-verification-standard/ |
| E09 | E09-02 Último CI | INFO | [{"conclusion": "", "createdAt": "2026-07-16T05:35:41Z", "headSha": "af2ad58fdb3d71e3bbb58cd1cf7df21cea152f64"}] | https://owasp.org/www-project-application-security-verification-standard/ |
| E09 | E09-03 Deploy portal Pages workflow | PASS | deploy-audit-portal.yml | GitHub Pages |
| E10 | E10-01 CORS allowlist Pages | PASS | ACAO='https://rdebiasec.github.io' | https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html |
| E10 | E10-02 CORS rechaza origen evil | PASS | ACAO='' | https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html |
| E10 | E10-03 Catálogo Pages 10/90/402 | PASS | {'guardrails': 10, 'agentes': 11, 'skills': 90, 'guias_contexto': 270, 'pasos': 402, 'items': 693} | integridad publicación |
| E10 | E10-04 Anti-wipe en GitHub Pages | PASS | merge=True | integridad publicación |

## Fuentes de método

- OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
- OWASP Secure Headers — https://owasp.org/www-project-secure-headers/
- OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- NIST SP 800-34 — https://csrc.nist.gov/pubs/sp/800/34/r1/final
- Render Postgres backups — https://render.com/docs/postgresql-backups
- Ley 1581/2012 — https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981


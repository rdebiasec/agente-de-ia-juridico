# Dictamen 20 expertos — hosting seguro y reputación (producción)

**Fecha:** 2026-07-16T16:19:52.036888+00:00
**Commit:** `293baf2`
**Target:** https://agente-de-ia-juridico.onrender.com
**Pages:** https://rdebiasec.github.io/agente-de-ia-juridico
**Oleadas:** [1, 2, 3, 4]
**Veredicto:** **GO** — PASS=62 WARN=0 FAIL=0 INFO=2

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
| E09 | Supply chain / CI-CD | PASS | todos PASS |
| E10 | Boundary / CORS / abuse | PASS | todos PASS |
| E11 | TLS / transport | PASS | todos PASS |
| E12 | Session & cookies | PASS | todos PASS |
| E13 | Rate limiting / abuse | PASS | todos PASS |
| E14 | Dependency / supply risk | PASS | todos PASS |
| E15 | Logging & forensics | PASS | todos PASS |
| E16 | Privacy ops (Ley 1581) | PASS | todos PASS |
| E17 | Data integrity | PASS | todos PASS |
| E18 | Multi-tenant isolation | PASS | todos PASS |
| E19 | Business continuity | PASS | todos PASS |
| E20 | Reputational / legal AI | PASS | E20-03:INFO |

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
| E05 | E05-03 Último backup Actions success | PASS | [{"conclusion": "success", "createdAt": "2026-07-16T09:10:43Z", "displayTitle": "Backup Postgres → R2"}] | https://render.com/docs/postgresql-backups |
| E06 | E06-01 .env no trackeado en git | PASS | tracked=none | https://owasp.org/www-project-application-security-verification-standard/ |
| E06 | E06-02 Auth web habilitada en prod | PASS | web_auth_enabled=True | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E06 | E06-03 Herramienta hash SITE_PASSWORD | PASS | hash_site_password.py | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html |
| E07 | E07-01 Health latency x3 < 15s | PASS | ms=[229, 232, 193] | https://render.com/docs |
| E07 | E07-02 OpenAI configurado | PASS | openai=True | ops |
| E07 | E07-03 Slack HITL canal | INFO | slack=False | ops |
| E08 | E08-01 Chat abogado alcanzable | PASS | HTTP 200 | producto |
| E08 | E08-02 Anti-wipe merge en portal | PASS | merge=True | integridad de datos |
| E08 | E08-03 Logout no borra cache local | PASS | wipe_helpers=False | integridad de datos |
| E09 | E09-01 CI workflow presente | PASS | ci.yml | https://owasp.org/www-project-application-security-verification-standard/ |
| E09 | E09-02 Último CI | PASS | [{"conclusion": "success", "createdAt": "2026-07-16T05:45:12Z", "headSha": "293baf2ffb483dae694f1f0094d4f6c7679c86d2"}] | https://owasp.org/www-project-application-security-verification-standard/ |
| E09 | E09-03 Deploy portal Pages workflow | PASS | deploy-audit-portal.yml | GitHub Pages |
| E10 | E10-01 CORS allowlist Pages | PASS | ACAO='https://rdebiasec.github.io' | https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html |
| E10 | E10-02 CORS rechaza origen evil | PASS | ACAO='' | https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html |
| E10 | E10-03 Catálogo Pages 10/90/402 | PASS | {'guardrails': 10, 'agentes': 11, 'skills': 90, 'guias_contexto': 270, 'pasos': 402, 'items': 693} | integridad publicación |
| E10 | E10-04 Anti-wipe en GitHub Pages | PASS | merge=True | integridad publicación |
| E11 | E11-01 Certificado TLS válido | PASS | tls=TLSv1.3 notAfter=Aug 24 22:01:50 2026 GMT | https://owasp.org/www-project-application-security-verification-standard/ |
| E11 | E11-02 CSP sin http:// en script-src | PASS |  'self' 'unsafe-inline' https://cdn.tailwindcss.com | https://owasp.org/www-project-secure-headers/ |
| E11 | E11-03 Portal sin assets http:// | PASS | http_asset_refs=0 | https://owasp.org/www-project-secure-headers/ |
| E12 | E12-01 Cookies HttpOnly en código | PASS | httponly_web=True httponly_audit=True | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html |
| E12 | E12-02 Cookies Secure vía cookie_secure() | PASS | secure_helper=True | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html |
| E12 | E12-03 Login fallido no setea sesión | PASS | HTTP 401 set-cookie_present=False | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html |
| E13 | E13-01 Middleware rate_limit presente | PASS | src/middleware/rate_limit.py | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E13 | E13-02 Audit login usa check_rate_limit | PASS | audit_portal_api rate hooks | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E13 | E13-03 Ráfaga prelogin fallido estable | PASS | codes=[401, 401, 401, 401, 401, 401] | https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html |
| E14 | E14-01 pyproject.toml presente | PASS | pyproject.toml | https://owasp.org/www-project-application-security-verification-standard/ |
| E14 | E14-02 CI instala dependencias | PASS | ci.yml install step | https://owasp.org/www-project-application-security-verification-standard/ |
| E14 | E14-03 Workflows sin secretos hardcodeados | PASS | hits=none | https://owasp.org/www-project-application-security-verification-standard/ |
| E15 | E15-01 Access log audit en API | PASS | audit_portal_access_log hooks | https://owasp.org/www-project-application-security-verification-standard/ |
| E15 | E15-02 401 progress sin leak de secretos | PASS | HTTP 401 body_snip='{"detail":"sesión de auditoría expirada o no autenticada."}' | https://owasp.org/www-project-application-security-verification-standard/ |
| E15 | E15-03 Modelo access_log / historial en storage | PASS | sql.py audit access/history tables | forensics |
| E16 | E16-01 Consentimiento 428 sin accept | PASS | login gates privacy+case data | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981 |
| E16 | E16-02 Contacto ARCO en policy | PASS | contact=privacidad@dbxsolutions.com | https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581 |
| E16 | E16-03 Páginas legales accesibles | PASS | privacidad + tratamiento-datos-casos | https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981 |
| E17 | E17-01 merge_audit_progress en servidor | PASS | src/gateway/audit_progress.py | integridad |
| E17 | E17-02 PUT progress usa merge | PASS | put_audit_progress merge call | integridad |
| E17 | E17-03 Tests anti-wipe merge | PASS | test_audit_progress_merge.py | integridad |
| E17 | E17-04 Anti-wipe frontend en prod | PASS | merge=True | integridad |
| E18 | E18-01 Test isolation progreso audit | PASS | test_audit_progress_history_and_isolation | https://owasp.org/www-project-application-security-verification-standard/ |
| E18 | E18-02 Progress exige auth | PASS | unauth progress denied | https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html |
| E18 | E18-03 Test cross-subject access control | PASS | test_plan_bola_blocks_cross_subject | https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html |
| E19 | E19-01 Workflow recover-from-r2 | PASS | recover-from-r2.yml (manual, no auto-restore) | https://csrc.nist.gov/pubs/sp/800/34/r1/final |
| E19 | E19-02 Script recover_from_r2.sh | PASS | scripts/dr/recover_from_r2.sh | https://render.com/docs/postgresql-backups |
| E19 | E19-03 R2 prod/ reachable | PASS | PRE audit-progress/ /                            PRE manifests/ /                            PRE postgres/ /                            PRE secrets/ / 2026-07-16 04:12:03        268 LATEST.txt | https://render.com/docs/postgresql-backups |
| E20 | E20-01 Guardrails g1–g10 en catálogo | PASS | ['g1', 'g10', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9'] | reputación jurídica |
| E20 | E20-02 Superficie chat con señal humana/HITL | PASS | HTTP 200 hitl_markers=True | IA propone; abogado aprueba |
| E20 | E20-03 Slack HITL gap conocido | INFO | slack_configured=False | ops |

## Fuentes de método

- OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
- OWASP Secure Headers — https://owasp.org/www-project-secure-headers/
- OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- NIST SP 800-34 — https://csrc.nist.gov/pubs/sp/800/34/r1/final
- Render Postgres backups — https://render.com/docs/postgresql-backups
- Ley 1581/2012 — https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981


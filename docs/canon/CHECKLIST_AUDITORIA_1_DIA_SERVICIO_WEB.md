# Checklist — Auditoría 1 día del servicio web

**Producto:** Firma virtual Lexiatek (penal-víctimas)  
**Duración objetivo:** 6–8 h (1 día)  
**Usar con:** `PROMPT_PANEL_12_ESPECIALISTAS_SERVICIO_WEB.md`  
**Fecha de plantilla:** 2026-08-05

Marcar: `[ ]` pendiente · `[x]` OK · `[~]` parcial · `[!]` falló

---

## Mañana (P0) — Acceso, privacidad, IA

### A. Runtime y superficies (30 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| A1 | Health prod OK + postgres | `curl -s https://agente-de-ia-juridico.onrender.com/health` | [x] |
| A2 | Environment=production | mismo JSON (`environment`) | [x] |
| A3 | Mapa superficies | Chat `/`, `/cliente`, `/auditoria`, `/legal/*`, Slack HITL | [x] |
| A4 | WhatsApp no activo | `ESTADO_PROYECTO.md` + ausencia gateway WA | [x] |

### B. AppSec / acceso (60–90 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| B1 | Auth web obligatoria en prod | `WEB_AUTH_ENABLED`, `SITE_PASSWORD`; `DEV_AUTO_LOGIN` off en prod | [!] |
| B2 | Sesión idle + cookie secure | `SESSION_IDLE_MINUTES`, `SESSION_COOKIE_SECURE`, `SESSION_SECRET` | [~] |
| B3 | Portal auditoría: login + PIN + consent | `/api/audit/login`, `prelogin`, `policy` | [!] |
| B4 | Allowlist emails auditoría | `AUDIT_ALLOWED_EMAILS` configurado en prod | [~] |
| B5 | IP allowlist (si aplica) | `IP_ALLOWLIST_ENABLED` / middleware | [x] |
| B6 | Sin secretos en git | `.gitignore` + no `.env` tracked; solo `.env.example` | [x] |
| B7 | APIs sensibles requieren sesión | chat, expediente, firma, audit progress | [!] |

### C. Privacidad Ley 1581 (60–90 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| C1 | Consent hard en login chat | `src/main.py` + `src/compliance/consent.py` | [!] |
| C2 | Consent portal + casos | `audit_portal_api.py` | [!] |
| C3 | Consent `/cliente` | `triple_chat_api.py` `consent_1581` | [x] |
| C4 | ARCO erase | `POST /api/compliance/arco-erase` + runbook | [~] |
| C5 | Páginas legales | `/legal/terminos`, privacidad, tratamiento casos | [x] |
| C6 | Retención programada | `purge_retention.py` / compliance retention | [x] |
| C7 | DPA encargados | `ESTADO_DPA_Y_ARCO.md` — firmados vs plantilla | [!] |
| C8 | Flags menores/sensibles | expediente `involucra_menor` / `datos_sensibles` | [x] |
| C9 | Cifrado en reposo | Fernet / `DATA_AT_REST_KEY` o derivado de `SESSION_SECRET` | [x] |

### D. Seguridad IA + HITL (60 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| D1 | I/O/T por agente en disco | `config/guardrails/agents/{id}/{input,output,tools}.md` | [x] |
| D2 | Cableado SDK | `sdk_guardrails.py` + `orchestrator.py` | [x] |
| D3 | Tutela/otro equipo → OOS | `triage.is_other_team_scope_request` + evals | [x] |
| D4 | Memoriales requieren plan HITL | `plan_templates` / runner / drafts | [x] |
| D5 | Disclaimer salida | apply_output_guardrails / g8=`aviso_borrador` | [x] |
| D6 | No inventar + pendiente | prompts + soft-flag invention | [x] |
| D7 | Tools chat sin redactor libre | superficie tools del POC | [x] |

---

## Tarde — Reliability, calidad, producto, claims

### E. SRE / reliability (45–60 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| E1 | Postgres prod healthy | Render DB + health `persistencia=postgres` | [x] |
| E2 | Alembic al día | `alembic_version` / migrate on boot | [~] |
| E3 | Backup offsite | `.github/workflows/backup-postgres.yml` último success | [x] |
| E4 | Restore documentado | `scripts/dr/*` + runbook | [x] |
| E5 | Fecha último restore drill | ops note | [~] |
| E6 | Drift config archivo↔DB | `sync_config_files.py --check` (prod secret) | [~] |
| E7 | Sin huérfanos tutela en `config_active` | query keys `%tutela%` = 0 | [x] |

### F. Calidad SW (45 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| F1 | CI verde en main | GitHub Actions | [!] |
| F2 | pytest guardrails/HITL/routing | `tests/test_guardrails_iot_*`, `test_firma`, evals | [x] |
| F3 | Evals OOS / memorial | `config/evals/agent_eval_cases.json` | [x] |
| F4 | Sync config en push | `sync-config.yml` | [x] |
| F5 | Catálogo portal = disco | `list_catalog_items` sin huérfanos | [~] |

### G. UX + marketing + ética (45 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| G1 | UI indica borrador / revisión humana | chat + firma | [x] |
| G2 | `/cliente` no sobrepromete | copy + gaps formacion | [x] |
| G3 | Entregables comerciales alineados | `docs/entregables/*` sin “tutela completa / abogado IA” | [!] |
| G4 | Prompts dicen “propone; abogado aprueba” | `sistema.md` / coordinador | [x] |

### H. FinOps + observabilidad + terceros (30–45 min)

| # | Check | Cómo / dónde | Resultado |
|---|---|---|---|
| H1 | Modelo high-risk ≠ default chat | `OPENAI_MODEL` vs `OPENAI_MODEL_HIGH_RISK` | [x] |
| H2 | Caps tokens/turns | `AGENT_MAX_*` en config | [x] |
| H3 | Sentry opcional + scrub | `SENTRY_DSN` / before_send | [~] |
| H4 | Estado DPA OpenAI/Render/Slack/R2 | `ESTADO_DPA_Y_ARCO.md` | [!] |

---

## Cierre del día (30 min)

1. Completar tabla de veredictos E1–E12.  
2. Top 10 acciones P0→P2.  
3. Declaración: **LISTO** | **LISTO CONDICIONAL** | **NO LISTO**.  
4. Guardar informe en `docs/canon/INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md` (o fecha).  
5. Si se tocó `audit-portal/`: smoke login local **y** prod.

---

## Comandos rápidos (sin secretos)

```bash
curl -sS https://agente-de-ia-juridico.onrender.com/health | python -m json.tool
gh run list --workflow=backup-postgres.yml --limit 3
gh run list --workflow=ci.yml --limit 5
pytest tests/test_guardrails_iot_coverage.py tests/test_firma.py -q
# Prod (con DATABASE_URL de secret, no loguear):
# SELECT count(*) FROM config_active WHERE key ILIKE '%tutela%';
```

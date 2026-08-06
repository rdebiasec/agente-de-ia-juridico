# Informe — Auditoría 12 especialistas (servicio web)

**Fecha:** 2026-08-05  
**Producto:** Firma virtual Lexiatek — `https://agente-de-ia-juridico.onrender.com`  
**Método:** Panel `PROMPT_PANEL_12_ESPECIALISTAS_SERVICIO_WEB.md` + checklist 1 día + evidencias runtime + dictamen [Auditar seguridad y compliance](c1c9cb43-ce60-4d0d-897e-72675e1ab95f)  
**Revalidado:** 2026-08-05 19:58 COT (runtime, browser, GitHub Actions y repo).  
**Remediación F4 P0 auth (parcial):** 2026-08-05 — acciones **1** y **7** aplicadas en código/blueprint + env live Render (`WEB_AUTH_ENABLED=true`, `AUDIT_REQUIRE_LOGIN=true`); smoke prod parcial OK. Resto de P0 (drafts, `web:test`, system_prompt, CI REQ) **pendiente**.  
**Declaración E0:** **NO LISTO** para escala comercial abierta (bloqueantes P0 restantes; auth web/portal en remediación).

---

## 1) Resumen ejecutivo

El servicio está **operativo** (health OK, Postgres, Slack socket, cifrado en reposo, backups R2 diarios, disclaimer HITL en salidas, tutela retirada del config store).  

Sin embargo, en la auditoría original producción tenía **`WEB_AUTH_ENABLED=false`** (fijado en `render.yaml`). **Estado remediación (2026-08-05):** blueprint + env Render pasan a `WEB_AUTH_ENABLED=true` y `AUDIT_REQUIRE_LOGIN=true`; default de código `audit_require_login=True` con bloqueo open-access en prod-like. Smoke post-deploy: `/health.web_auth_enabled=true`, `/api/audit/session` sin open-access, `POST /chat` → 401. Hallazgos aún abiertos salvo auth/portal — dentro de la IP (histórico):

- `POST /chat` responde sin login (y puede filtrar `system_prompt` en traza).
- `GET /drafts` lista borradores con **contenido completo**; PDF/DOCX descargables.
- Sujeto compartido `web:test` colisiona historial entre operadores.
- ARCO acepta `?user_id=` arbitrario sin cookie firme.
- Consent hard de login **no se aplica** (login cortocircuita).

| Especialista | Veredicto | #P0 | #P1 | #P2 |
|---|---|---:|---:|---:|
| E1 AppSec | **FAIL** | 4 | 2 | 1 |
| E2 Privacidad 1581 | **FAIL** | 2 | 2 | 1 |
| E3 Seguridad IA + HITL | **PARTIAL** | 1 | 1 | 1 |
| E4 Arquitectura | **PASS** | 0 | 0 | 1 |
| E5 SRE / Reliability | **PASS** | 0 | 0 | 1 |
| E6 Calidad SW | **FAIL** | 1 | 0 | 1 |
| E7 UX producto | **FAIL** | 1 | 1 | 0 |
| E8 Marketing / claims | **PARTIAL** | 0 | 1 | 1 |
| E9 Ética litigante | **PARTIAL** | 1 | 0 | 0 |
| E10 FinOps | **PARTIAL** | 0 | 1 | 1 |
| E11 Observabilidad | **PARTIAL** | 0 | 0 | 1 |
| E12 Supply chain | **PARTIAL** | 0 | 2 | 1 |

**Conteo actualizado:** P0×10 · P1×10 · P2×9

---

## 2) Evidencias clave (runtime)

```json
GET /health → {
  "status": "ok",
  "environment": "production",
  "persistencia": "postgres",
  "web_auth_enabled": false,      // ← P0
  "dev_auto_login": false,        // OK
  "ip_allowlist_enabled": true,   // mitiga, no sustituye auth
  "at_rest_encryption": true,     // OK
  "slack_socket_started": true,
  "twilio_configured": false      // WhatsApp/SMS off — OK
}
```

| Check | Resultado |
|---|---|
| `/legal/terminos` | HTTP 200 |
| `/auditoria/` | HTTP 200 |
| `/login` | HTTP 302 |
| `/` (chat UI) | HTTP 302 |
| `/cliente` | HTTP 200 (superficie víctima; esperable con consent propio) |
| `POST /chat` sin cookie | **HTTP 200 + respuesta LLM + traza completa** |
| Backup Postgres→R2 | success 2026-08-05 (y días previos) |
| CI `main` | **failure** — `validate_fase0.py`: espera 50 REQ, hay 45 |
| `config_active` tutela/constitucional | **0** rows (prod limpio) |
| pytest F3 config+guardrails+HITL | **52 passed** |
| pytest F4 acceso+privacidad+HITL | **45 passed** (fixtures fijan explícitamente el modo autenticado) |

### Revalidación directa F4

Desde un navegador en la IP autorizada, sin ingresar correo, contraseña ni PIN:

```json
GET /api/audit/session → {
  "auth_enabled": true,
  "authenticated": true,
  "email": "editor@lexiatek.local",
  "login_required": false,
  "open_access": true
}
```

El editor cargó el catálogo activo y habilitó controles de edición/guardado. Esto confirma que la IP allowlist es el único perímetro real del portal: no hay identidad individual, consentimiento ni PIN antes de editar configuración.

Revalidación operativa adicional:

- `/health`: Postgres, cifrado y Slack OK; `web_auth_enabled=false`, `ip_allowlist_enabled=true`.
- Backup Postgres→R2: 5/5 ejecuciones recientes exitosas (1–5 agosto).
- CI `main`: 5/5 ejecuciones recientes fallidas; la última exige 50 REQ pero el canon tiene 45.
- Catálogo prod: 0 coincidencias `tutela`/`constitucional`.

---

## 3) Hallazgos por especialista

### [E1][P0] Auth web desactivada en producción
- **Veredicto:** FAIL → **REMEDIADO** (código + Render env + smoke prod)  
- **Evidencia (auditoría):** `/health` → `web_auth_enabled: false`; `render.yaml`; `POST /chat` 200 sin sesión.  
- **Riesgo:** Cualquier cliente en IP allowlist usa el despacho.  
- **Remedio aplicado:** `WEB_AUTH_ENABLED=true` en Render live + `render.yaml`; smoke: `web_auth_enabled=true`, `POST /chat` → 401.  

### [E1][P0] Bandeja HITL `/drafts*` expone relatos y descargas
- **Veredicto:** FAIL  
- **Evidencia:** `GET /drafts` 200 con `contenido`; `GET /drafts/{id}/pdf|docx` 200; `firma_api.py`.  
- **Riesgo:** Confidencialidad de víctimas rota dentro de la IP allowlist.  
- **Remedio:** Atar lista/PDF/DOCX/approve/reject a `subject_id` de sesión real; nunca listar global sin auth.  

### [E1][P0] Traza de `/chat` expone system prompt
- **Evidencia:** JSON incluye `trace.completion.calls[].system_prompt`.  
- **Remedio:** No devolver prompts/internals al cliente; debug solo autenticado.  

### [E1][P0] Sujeto compartido `web:test` con auth off
- **Evidencia:** `src/auth/deps.py`; historial/`session_id` colisionan entre operadores.  
- **Remedio:** Eliminar fallback `web:test` en prod; exigir cookie firmada.  

### [E1][P1] ARCO con `?user_id=` arbitrario
- **Evidencia:** `POST /api/compliance/arco-erase?user_id=…` → 200; `compliance_api.py`.  
- **Remedio:** ARCO solo con cookie/sesión; rechazar override en prod.  

### [E1][P1] `/cliente` y `/webchat` bypassean IP allowlist
- **Evidencia:** `ip_allowlist.py` L69–73.  
- **Remedio:** Quitar bypass en prod o feature-flag + auth propia.  

### [E1][P2] Sin rate limit en `POST /chat`
- **Remedio:** Añadir `check_rate_limit` como en login/plan.  

### [E2][P0] Consent hard no aplica con auth off
- **Evidencia:** Login cortocircuita (`main.py` L483–486) vs runbook 1581.  

### [E2][P0] Datos de caso en `/drafts` sin identidad
- **Evidencia:** misma que E1 drafts.  

### [E2][P1] DPA encargados pendientes (OpenAI/Render/Slack)
- **Evidencia:** `ESTADO_DPA_Y_ARCO.md`. Slack HITL ya está live → priorizar.  

### [E2][P1] ARCO vs backups R2 / sujeto débil
- **Remedio:** Documentar purga offsite; ARCO solo cookie.  

### [E2][P2] Correo ARCO inconsistente (`contacto@` vs `privacidad@`)
- **Evidencia:** `policy.py` vs runbook.  

### [E3][P0] Aprobar/rechazar borradores sin identidad real
- **Evidencia:** `firma_api` + `require_web_session` no-op.  

### [E3][P1] Chat libre sin rate limit (FinOps/abuso)  
### [E3][P2] Soft-flag invención — aceptable con HITL+auth  
- OOS tutela: **PASS** (probe + 0 keys en DB).  

### [E4][PASS] Arquitectura firma virtual coherente
- **P2:** `/cliente` bypass allowlist vs runbook “no publicar a prod”.  

### [E5][PASS] Health + backups R2 + recover workflow
- **P2:** Restore drill sin fecha reciente ensayada.  

### [E6][P0] CI main en rojo (`validate_fase0` 50 vs 45 REQ)
- Suite local auth/firma/guardrails: 22 passed (no sustituye CI).  
- **P2:** defaults permisivos en `.env.example`.  

### [E7][P0] Portal auditoría entra como editor compartido sin login/PIN/consent
- **Veredicto:** FAIL → **REMEDIADO** (código + Render env + smoke session; login PIN/prod con credenciales humano pendiente)  
- **Evidencia (auditoría):** `/api/audit/session` devolvía `authenticated=true`, `email=editor@lexiatek.local`, `open_access=true`; default `AUDIT_REQUIRE_LOGIN=false`.
- **Riesgo:** cualquier persona en la IP autorizada podía editar config bajo identidad compartida.
- **Remedio aplicado:** `AUDIT_REQUIRE_LOGIN=true` en Render live + `render.yaml`; default `audit_require_login=True`; open-access forzado OFF si `RENDER` o `SESSION_COOKIE_SECURE`. Smoke: `login_required=true`, `open_access=false`, `authenticated=false`.
- **Pendiente:** smoke login correo+password+PIN+consent con credenciales reales; confirmar allowlist `AUDIT_ALLOWED_EMAILS`.

### [E7][P1] Threat model `/cliente` público  

### [E8][P1] Marketing aún menciona “tutela completa”
- **Evidencia:** `presentacion-dbx-solutions-valor-producto.md`.  

### [E9][P0] Exposición de relatos de víctimas vía `/drafts` (ética confidencialidad)
- Modelo “IA propone / abogado aprueba”: OK en prompts; roto en la práctica por API abierta.  

### [E10][P1] Riesgo gasto OpenAI (chat abierto + sin rate limit)  
### [E11][P2] Sentry opcional no verificable en health  
### [E12][P1] DPA OpenAI/Render/Slack  
### [E12][P2] Sin Dependabot / lockfile  

---

## 4) Top 10 acciones (orden de ejecución)

| # | Acción | Sev | Esfuerzo | Estado |
|---|---|---|---|---|
| 1 | `WEB_AUTH_ENABLED=true` en Render **y** `render.yaml` | P0 | S | **HECHO** (env live + blueprint + smoke) |
| 2 | Atar `/drafts*` (lista, PDF, DOCX, approve/reject) a sesión real | P0 | M | **HECHO** (BOLA `web:{subject_id}`; 403 cross-subject) |
| 3 | Eliminar `web:test` / `user_id` query en prod (chat + ARCO) | P0 | M | **HECHO** (auth ON + validate_production + 503 si auth off en prod) |
| 4 | Redactar respuesta `/chat`: sin `system_prompt` ni internals | P0 | M | **HECHO** (runner + `public_trace` en chat/history/debug) |
| 5 | Consent hard otra vez camino real (login no cortocircuita) | P0 | S | **HECHO** (desbloqueado con auth; login exige privacy+casos) |
| 6 | Arreglar `validate_fase0` (45 REQ) → CI verde | P0 | S | **HECHO** (`REQ_ACTIVOS_ESPERADOS = 45`) |
| 7 | `AUDIT_REQUIRE_LOGIN=true` + allowlist emails + PIN | P0 | S | **HECHO** (env/blueprint/código; smoke session OK; login PIN humano) |
| 8 | Rate limit `POST /chat` + revisar bypass `/cliente` | P1 | M | pendiente |
| 9 | Cerrar DPA OpenAI/Render/Slack; unificar correo ARCO | P1 | M (humano) | pendiente |
| 10 | Limpiar claims “tutela” en entregables + restore drill fechado | P1 | S–M | pendiente |

---

## 5) Qué ya está bien (no reabrir)

- Postgres prod + cifrado en reposo (`at_rest_encryption: true`).  
- Backups diarios cifrados → R2 (último success hoy).  
- `dev_auto_login: false` en prod.  
- WhatsApp/Twilio off.  
- Disclaimer HITL en salidas.  
- Guardrails I/O/T + desk_policies; `g*` solo alias deprecados.  
- Config store sin skills/agente tutela (0 keys).  
- Páginas legales accesibles.  
- Slack socket HITL arriba.

---

## 6) Declaración final (E0)

**LISTO CONDICIONAL** para escala controlada cerrada: acciones P0 **1–7** cerradas en código/blueprint (auth web+portal, drafts BOLA, sin `web:test` en prod, sin filtrar prompts, consent en login, CI `validate_fase0` 45 REQ). Quedan P1 (rate limit `/cliente`, DPA, claims tutela).

~~**NO LISTO**~~ (histórico 2026-08-05) hasta cerrar acciones 1–7.  

**Nota:** asumir que cualquier dispositivo en la IP allowlist pudo leer borradores en revisión; rotar exposición operativa si hubo datos reales en `/drafts`.

---

## 7) Fuentes oficiales de la recomendación

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — autenticación, sesiones y control de acceso consistentes; sustenta E1/E7.
- [OWASP API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) — cada acceso por ID debe verificar autorización sobre el objeto; sustenta aislamiento de drafts, expedientes y ARCO.
- [SUIN-Juriscol — régimen de protección de datos / Ley 1581](https://www.suin-juriscol.gov.co/legislacion/habeasdata.html) — autorización previa e informada, circulación restringida y responsabilidad demostrada; sustenta E2.
- [OpenAI Agents SDK — Human in the loop](https://openai.github.io/openai-agents-python/human_in_the_loop/) y [Guardrails](https://openai.github.io/openai-agents-python/guardrails/) — pausa/aprobación de acciones sensibles y límites de guardrails de agente/tool; sustenta E3.
- [Render — compliance y DPA](https://render.com/docs/certifications-compliance) — DPA disponible en Document Center; sustenta la acción de cerrar evidencia del encargado.
- Evidencia operativa: [CI fallida más reciente](https://github.com/rdebiasec/agente-de-ia-juridico/actions/runs/31053690978) · [backup R2 exitoso más reciente](https://github.com/rdebiasec/agente-de-ia-juridico/actions/runs/30993803826).

Fuentes internas canónicas: `GUIA_PROYECTO_AGENTE_JURIDICO.md`, `requisitos_asistente.json`, `ESTADO_PROYECTO.md`, `RUNBOOK_CUMPLIMIENTO_1581.md`, `ESTADO_DPA_Y_ARCO.md`.

---

## 8) Artefactos generados en esta sesión

| Archivo | Uso |
|---|---|
| `docs/canon/PROMPT_PANEL_12_ESPECIALISTAS_SERVICIO_WEB.md` | Prompt multi-especialista reutilizable |
| `docs/canon/CHECKLIST_AUDITORIA_1_DIA_SERVICIO_WEB.md` | Checklist operativo 1 día |
| `docs/canon/INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md` | Este informe |

**Siguiente paso recomendado:** redeploy Render con este PR; smoke auth local+prod; P1 rate limit `/cliente` + DPA.

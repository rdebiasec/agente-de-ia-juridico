# Informe — Auditoría 12 especialistas (servicio web)

**Fecha:** 2026-08-05  
**Producto:** Firma virtual Lexiatek — `https://agente-de-ia-juridico.onrender.com`  
**Método:** Panel `PROMPT_PANEL_12_ESPECIALISTAS_SERVICIO_WEB.md` + checklist 1 día + evidencias runtime + dictamen [Auditar seguridad y compliance](c1c9cb43-ce60-4d0d-897e-72675e1ab95f)  
**Declaración E0:** **NO LISTO** para escala comercial abierta (bloqueantes P0 de acceso y confidencialidad).

---

## 1) Resumen ejecutivo

El servicio está **operativo** (health OK, Postgres, Slack socket, cifrado en reposo, backups R2 diarios, disclaimer HITL en salidas, tutela retirada del config store).  

Sin embargo, en producción **`WEB_AUTH_ENABLED=false`** (fijado en `render.yaml`). El gate efectivo es solo **IP allowlist**. Dentro de esa IP:

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
| E7 UX producto | **PARTIAL** | 0 | 2 | 0 |
| E8 Marketing / claims | **PARTIAL** | 0 | 1 | 1 |
| E9 Ética litigante | **PARTIAL** | 1 | 0 | 0 |
| E10 FinOps | **PARTIAL** | 0 | 1 | 1 |
| E11 Observabilidad | **PARTIAL** | 0 | 0 | 1 |
| E12 Supply chain | **PARTIAL** | 0 | 2 | 1 |

**Conteo actualizado:** P0×9 · P1×11 · P2×9

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
| pytest local auth+guardrails+firma | **22 passed** |

---

## 3) Hallazgos por especialista

### [E1][P0] Auth web desactivada en producción
- **Veredicto:** FAIL  
- **Evidencia:** `/health` → `web_auth_enabled: false`; `render.yaml` L38–39; `require_web_session` no-op (`src/auth/deps.py`); `POST /chat` 200 sin sesión.  
- **Riesgo:** Cualquier cliente en IP allowlist usa el despacho.  
- **Remedio:** `WEB_AUTH_ENABLED=true` en Render + blueprint; smoke 401/302 sin cookie.  

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

### [E7][P1] Portal auditoría: login 503 / gate débil
- **Evidencia:** `POST /api/audit/login` 503 si `auth_enabled` false; `AUDIT_REQUIRE_LOGIN` no forzado en blueprint.  
- **Remedio:** `AUDIT_REQUIRE_LOGIN=true`; desacoplar gate portal de `WEB_AUTH`.  

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

| # | Acción | Sev | Esfuerzo |
|---|---|---|---|
| 1 | `WEB_AUTH_ENABLED=true` en Render **y** `render.yaml` | P0 | S |
| 2 | Atar `/drafts*` (lista, PDF, DOCX, approve/reject) a sesión real | P0 | M |
| 3 | Eliminar `web:test` / `user_id` query en prod (chat + ARCO) | P0 | M |
| 4 | Redactar respuesta `/chat`: sin `system_prompt` ni internals | P0 | M |
| 5 | Consent hard otra vez camino real (login no cortocircuita) | P0 | S |
| 6 | Arreglar `validate_fase0` (45 REQ) → CI verde | P0 | S |
| 7 | `AUDIT_REQUIRE_LOGIN=true` + allowlist emails + PIN | P1 | S |
| 8 | Rate limit `POST /chat` + revisar bypass `/cliente` | P1 | M |
| 9 | Cerrar DPA OpenAI/Render/Slack; unificar correo ARCO | P1 | M (humano) |
| 10 | Limpiar claims “tutela” en entregables + restore drill fechado | P1 | S–M |

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

**NO LISTO** para invitar más despachos / tráfico abierto hasta cerrar **acciones 1–5** (auth, drafts por sujeto, sin `web:test`/ARCO débil, sin filtrar prompts, consent real).  

Con 1–6 hechas → **LISTO CONDICIONAL** (faltan portal audit duro, rate limit, DPA).  
Con 1–9 hechas → **LISTO** para escala controlada.  

**Nota:** asumir que cualquier dispositivo en la IP allowlist pudo leer borradores en revisión; rotar exposición operativa si hubo datos reales en `/drafts`.

---

## 7) Artefactos generados en esta sesión

| Archivo | Uso |
|---|---|
| `docs/canon/PROMPT_PANEL_12_ESPECIALISTAS_SERVICIO_WEB.md` | Prompt multi-especialista reutilizable |
| `docs/canon/CHECKLIST_AUDITORIA_1_DIA_SERVICIO_WEB.md` | Checklist operativo 1 día |
| `docs/canon/INFORME_AUDITORIA_12_ESPECIALISTAS_SERVICIO_WEB.md` | Este informe |

**Siguiente paso recomendado (Agent mode):** aplicar acciones 1, 3 y 4 en código/blueprint y redeploy; luego smoke auth local+prod.

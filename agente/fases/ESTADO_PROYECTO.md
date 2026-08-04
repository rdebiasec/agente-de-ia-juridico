# Estado del proyecto — firma virtual (actualizado 2026-08-03)

Fuente sagrada: `agente/fuente/GUIA_PROYECTO_AGENTE_JURIDICO.md` y `agente/requisitos/requisitos_asistente.json`.

El roadmap original (Fases 0→3 por gating) fue **reemplazado operativamente** por el modelo **firma virtual** (`docs/canon/plan-rediseno-firma.md`): todos los agentes activos, supervisión humana (HITL), persistencia Postgres en dev==prod.

**Voz de despacho (POC):** `coordinador_caso` es el único interlocutor en web/Slack. Los **9 especialistas** operan como **backoffice** (`Agent.as_tool` + trazas); el chat no los expone como caras distintas.

**Cadenas = planes/tools; sin handoffs peer:** flujos frecuentes SPOA (indagación/impulso, VIF, querella/abreviado) se orquestan por plantillas en `plan_templates.py` (ver `docs/canon/flujos-frecuentes-penal-victimas-co.md`).

**Alcance producto (2026-08-03):** denuncias / representación penal-víctimas; derecho de petición, memoriales e impulso como herramientas **penales**. La acción de tutela (especialista constitucional y REQ-038…042) quedó **fuera del producto**.

**Cumplimiento Ley 1581 (2026-07-21):** consentimiento hard en `/auth/login`; ARCO web `POST /api/compliance/arco-erase`; retención mensual; términos `/legal/terminos`; cifrado en reposo (Fernet via `DATA_AT_REST_KEY`/`SESSION_SECRET`); flags `involucra_menor`/`datos_sensibles` en expediente; plantillas DPA/RNBD en `docs/operaciones/`.

**Config live (2026-07-24):** editor `/auditoria/` versiona prompts, guardrails (texto) y skills en Postgres. Allowlist opcional `AUDIT_ALLOWED_EMAILS`. Idle sesión default **60 min**. Observabilidad opcional: `SENTRY_DSN` (scrub PII via `before_send`).

**Modelos (batch Udemy 2026-07-31, Opción A):** default/laborers `gpt-4.1-mini` @ temp 0.2 · high-risk (redactor) `gpt-4.1` @ temp 0.1 · RunContext tipado + costo estimado en traza.

**Auditoría Gerente + agentes (vivo):** `docs/auditoria/AUDITORIA_GERENTE_Y_AGENTES.md` — G01–G09 **hecho** (2026-07-31). **Bitácora de notas** (Gerente maestra + especialistas) en `Expediente.bitacora`; Drive diferido.

## Resumen ejecutivo

| Bloque | Estado | Notas |
|--------|--------|-------|
| **Fase A — Firma sin estado** | ✅ Cerrada | Orquestador, 9 roles, KB, playbooks CGP/906, guardrails, web |
| **Fase B — Persistencia** | ✅ Mayoría | Postgres, Alembic, RAG, HITL borradores, PDF/DOCX, plazos, scheduler |
| **Sesiones multi-turno** | ✅ | `chat_sessions`, idle configurable, reset chat, historial servidor en UI; G01 persiste también `plan_required` |
| **Editor de configuración** | ✅ | Prompts / guardrails / skills versionados; G08 parity checksum al boot |
| **Canales producción** | 🟡 Parcial | Web ✅ · Slack HITL en Render ✅ (`slack_socket_started`) · WhatsApp **no** |
| **45 requisitos (REQ)** | 🟡 Por validar | Tablero: `docs/operaciones/CHECKLIST_REQ_CIERRE.md` (REQ-038…042 retirados) |

## Hecho (evidencia en repo)

### Fundamentos (KAN-5, KAN-9, KAN-10) — REQ-001…011
- Perfil y tono: `agente/prompts/sistema.md`
- Áreas y normas: `agente/conocimiento/*.md`
- Tools: `src/mcp/tools.py` (`listar_areas_derecho`, playbooks, RAG)

### Firma de agentes (plan Fase A)
- `src/agents/orchestrator.py` — POC `coordinador_caso` + **9 especialistas** como tools internas (backoffice)
- Salidas estructuradas: `src/agents/schemas.py` (documentos penales / calidad; sin schema Tutela)
- Sin gating por fase: `src/agents/guardrails.py`
- Runner: payload `agent` = POC; `trace.sent_to_agent` / `selected_agent` = especialista de auditoría

### Persistencia y firma operativa (plan Fase B)
- Postgres + pgvector: `src/storage/sql.py`, `deploy/docker-compose.yml`, `render.yaml`
- Migraciones: `0001`…`0007` (config store)
- HITL: `src/hitl/drafts.py`, bandeja `static/firma.js`, API `src/gateway/firma_api.py`
- Slack revisión: `src/hitl/slack_review.py`, `src/gateway/slack_interactivity.py` (requiere env)
- RAG: `src/services/rag.py`, ingest KB, búsqueda en bandeja
- Documentos: `src/services/documentos.py` (PDF/DOCX, extracción)
- Plazos: `src/services/plazos.py`, scheduler `src/services/scheduler.py`
- Expediente: `src/gateway/expediente.py` + **sync desde chat** `src/services/expediente_sync.py`

### Conversación y trazabilidad (extensión reciente)
- Multi-turno: `src/gateway/agent_session.py`, `RepositoryAgentSession`
- Validaciones encadenadas: `src/agents/pipeline.py`
- Trazas enriquecidas: `src/agents/runner.py` (spans, session_flow, RAG prefetch)
- UI: panel Workflow Trace + timeline de sesión (`static/chat.js`)
- APIs: `POST /chat/reset`, `GET /chat/history`, `GET /debug/trace/{session_id}`
- Historial servidor al abrir chat + toast; adjuntos indexan expediente

### Despliegue
- Producción: `https://agente-de-ia-juridico.onrender.com` — `persistencia: postgres`
- Local: `./scripts/start-local.sh` (Docker + fallback memoria)

## Pendiente prioritario (siguiente sprint)

### P0 — Operación despacho
1. **Checklist REQ** — pruebas en JSON / `docs/operaciones/CHECKLIST_REQ_CIERRE.md` (sin tutelas).
2. **DPA firmados** — evidencia en `docs/operaciones/ESTADO_DPA_Y_ARCO.md`.
3. **Medir tokens (B13)** — tras 1–2 semanas con costo en traza, tunear `SESSION_RECENT_MESSAGES` / `SESSION_SUMMARY_MAX_CHARS` (`docs/operaciones/FORECAST_COSTOS_TURNOS.md`).

### P1 — Acceso
4. Configurar `AUDIT_ALLOWED_EMAILS` en prod (ver `docs/operaciones/CUENTAS_POR_ABOGADO.md`).
5. Opcional: `SENTRY_DSN` + `pip install '.[observability]'`.
6. Cuentas por abogado (password individual) — roadmap, no código aún.

### P2 — Producto restante
7. REQ-043…047 seguimiento / informes.
8. Derecho de petición / impulso / seguimiento ante mora de respuesta (vía penal, no constitucional).

### P3 — Canales
9. **WhatsApp** — no construir sin evaluación 1581/2300.

### Hecho reciente (ops)
- Slack HITL prod: `slack_socket_started=true` — runbook `docs/operaciones/SLACK_HITL_RENDER.md`.
- Auditoría Gerente G01–G09 (persistencia, triage, parity, cache, vecinos).
- Retiro de tutela del producto (especialista + REQ-038…042).

## Documentos históricos (no borrar, contexto)

| Archivo | Estado |
|---------|--------|
| `agente/fases/FASE_0.md` | Cerrada — `ACTA_CIERRE_FASE_0.md` |
| `agente/fases/FASE_1.md` | **Obsoleta** (gating); capacidades viven en firma |
| `agente/fases/FASE_2.md` | Stub roadmap |
| `agente/fases/FASE_3.md` | Stub roadmap; conceptos/memoriales en agentes (tutela retirada del producto) |
| `docs/canon/plan-rediseno-firma.md` | Plan maestro técnico |
| `docs/canon/plan-udemy-agents-sdk-aplicacion.md` | Tablero Udemy → producto (28 lecciones, orden pedagógico propósito-primero); clase → mapa → «aprobado, ejecuta» |
| `docs/canon/PLAN_UDEMY_CORTO.md` / `PROMPT_CLASE_UDEMY.md` | Orden corto + prompt de clase; registro en `REGISTRO_UDEMY_REVISIONES.md` |

## Criterio de “siguiente entrega” recomendada

**Entrega C — Impulso / seguimiento ante mora de petición**
- 3+ turnos de chat con expediente auto-actualizado
- Traza con 20+ spans y timeline de sesión
- Borrador de impulso/seguimiento ante silencio a derecho de petición → aprobar en HITL
- Misma prueba en local y Render

## Comandos útiles

```bash
./scripts/start-local.sh          # app + postgres
./scripts/local_db.sh --ingest    # KB en RAG
pytest tests/ -q                  # suite
curl -s localhost:8000/health
```

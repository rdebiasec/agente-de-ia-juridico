# Estado del proyecto — firma virtual (actualizado 2026-07-20)

Fuente sagrada: `agente/fuente/GUIA_PROYECTO_AGENTE_JURIDICO.md` y `agente/requisitos/requisitos_asistente.json`.

El roadmap original (Fases 0→3 por gating) fue **reemplazado operativamente** por el modelo **firma virtual** (`docs/canon/plan-rediseno-firma.md`): todos los agentes activos, supervisión humana (HITL), persistencia Postgres en dev==prod.

**Voz de despacho (POC):** `coordinador_expediente_penal` es el único interlocutor en web/Slack. Los 10 especialistas operan como **backoffice** (`Agent.as_tool` + trazas); el chat no los expone como caras distintas.

**Cadenas = planes/tools; sin handoffs peer:** flujos frecuentes SPOA (indagación/impulso, VIF, querella/abreviado) se orquestan por plantillas en `plan_templates.py` (ver `docs/canon/flujos-frecuentes-penal-victimas-co.md`).

**Cumplimiento Ley 1581 (2026-07-21):** consentimiento hard en `/auth/login`; ARCO web `POST /api/compliance/arco-erase`; retención mensual; términos `/legal/terminos`; cifrado en reposo (Fernet via `DATA_AT_REST_KEY`/`SESSION_SECRET`); flags `involucra_menor`/`datos_sensibles` en expediente; plantillas DPA/RNBD en `docs/operaciones/`.

**Config live (2026-07-24):** editor `/auditoria/` versiona prompts, guardrails (texto) y skills en Postgres. Allowlist opcional `AUDIT_ALLOWED_EMAILS`. Idle sesión default **60 min**. Observabilidad opcional: `SENTRY_DSN`.

## Resumen ejecutivo

| Bloque | Estado | Notas |
|--------|--------|-------|
| **Fase A — Firma sin estado** | ✅ Cerrada | Orquestador, 10 roles, KB, playbooks CGP/906, guardrails, web |
| **Fase B — Persistencia** | ✅ Mayoría | Postgres, Alembic, RAG, HITL borradores, PDF/DOCX, plazos, scheduler |
| **Sesiones multi-turno** | ✅ | `chat_sessions`, idle configurable, reset chat, historial servidor en UI |
| **Editor de configuración** | ✅ | Prompts / guardrails / skills versionados |
| **Canales producción** | 🟡 Parcial | Web ✅ · Slack HITL (Aprobar/Editar/Rechazar + allowlist) — falta `SLACK_APP_TOKEN`/`SLACK_APPROVER_IDS` en Render · WhatsApp **no** |
| **50 requisitos (REQ)** | 🟡 Por validar | Tablero: `docs/operaciones/CHECKLIST_REQ_CIERRE.md` |

## Hecho (evidencia en repo)

### Fundamentos (KAN-5, KAN-9, KAN-10) — REQ-001…011
- Perfil y tono: `agente/prompts/sistema.md`
- Áreas y normas: `agente/conocimiento/*.md`
- Tools: `src/mcp/tools.py` (`listar_areas_derecho`, playbooks, RAG)

### Firma de agentes (plan Fase A)
- `src/agents/orchestrator.py` — POC `coordinador_expediente_penal` + 10 especialistas como tools internas (backoffice)
- Salidas estructuradas: `src/agents/schemas.py` (incl. `Tutela` en evaluador constitucional)
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
1. **Slack HITL en producción** — configurar `SLACK_APP_TOKEN` (`xapp`) en Render; verificar `/health.slack_socket_started`.
2. **Checklist REQ-001…050** — pruebas en JSON / `docs/operaciones/CHECKLIST_REQ_CIERRE.md`.
3. **DPA firmados** — evidencia en `docs/operaciones/ESTADO_DPA_Y_ARCO.md`.

### P1 — Acceso
4. Configurar `AUDIT_ALLOWED_EMAILS` en prod (ver `docs/operaciones/CUENTAS_POR_ABOGADO.md`).
5. Opcional: `SENTRY_DSN` + `pip install '.[observability]'`.
6. Cuentas por abogado (password individual) — roadmap, no código aún.

### P2 — Producto restante
7. Tutela: término 10 días al aprobar + prueba E2E.
8. REQ-043…047 seguimiento / informes.

### P3 — Canales
9. **WhatsApp** — no construir sin evaluación 1581/2300.

## Documentos históricos (no borrar, contexto)

| Archivo | Estado |
|---------|--------|
| `agente/fases/FASE_0.md` | Cerrada — `ACTA_CIERRE_FASE_0.md` |
| `agente/fases/FASE_1.md` | **Obsoleta** (gating); capacidades viven en firma |
| `agente/fases/FASE_2.md` | Stub roadmap |
| `agente/fases/FASE_3.md` | Stub roadmap; tutelas/conceptos ya en agentes |
| `docs/canon/plan-rediseno-firma.md` | Plan maestro técnico |
| `docs/canon/plan-udemy-agents-sdk-aplicacion.md` | Tablero Udemy → producto (28 lecciones, orden pedagógico propósito-primero); clase → mapa → «aprobado, ejecuta» |
| `docs/canon/PLAN_UDEMY_CORTO.md` / `PROMPT_CLASE_UDEMY.md` | Orden corto + prompt de clase; registro en `REGISTRO_UDEMY_REVISIONES.md` |

## Criterio de “siguiente entrega” recomendada

**Entrega C — Tutela con continuidad verificable**
- 3+ turnos de chat con expediente auto-actualizado
- Traza con 20+ spans y timeline de sesión
- Borrador tutela en bandeja → aprobar → término 10 días en Postgres
- Misma prueba en local y Render

## Comandos útiles

```bash
./scripts/start-local.sh          # app + postgres
./scripts/local_db.sh --ingest    # KB en RAG
pytest tests/ -q                  # suite
curl -s localhost:8000/health
```

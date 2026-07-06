# Estado del proyecto — firma virtual (actualizado 2026-06-29)

Fuente sagrada: `agente/fuente/GUIA_PROYECTO_AGENTE_JURIDICO.md` y `agente/requisitos/requisitos_asistente.json`.

El roadmap original (Fases 0→3 por gating) fue **reemplazado operativamente** por el modelo **firma virtual** (`docs/canon/plan-rediseno-firma.md`): todos los agentes activos, supervisión humana (HITL), persistencia Postgres en dev==prod.

## Resumen ejecutivo

| Bloque | Estado | Notas |
|--------|--------|-------|
| **Fase A — Firma sin estado** | ✅ Cerrada | Orquestador, 10 roles, KB, playbooks CGP/906, guardrails, web |
| **Fase B — Persistencia** | ✅ Mayoría | Postgres, Alembic, RAG, HITL borradores, PDF/DOCX, plazos, scheduler |
| **Sesiones multi-turno** | ✅ | `chat_sessions`, 6 h idle, reset chat, trazas largas + continuidad |
| **Canales producción** | 🟡 Parcial | Web ✅ · Slack código listo, **sin token en prod** · WhatsApp **no implementado** |
| **50 requisitos (REQ)** | 🟡 Por validar | Capacidades en agentes; falta checklist formal REQ→prueba |

## Hecho (evidencia en repo)

### Fundamentos (KAN-5, KAN-9, KAN-10) — REQ-001…011
- Perfil y tono: `agente/prompts/sistema.md`
- Áreas y normas: `agente/conocimiento/*.md`
- Tools: `src/mcp/tools.py` (`listar_areas_derecho`, playbooks, RAG)

### Firma de agentes (plan Fase A)
- `src/agents/orchestrator.py` — intake, estratega, civil, penal, redacción, conceptos, tutela, dependiente, comunicación
- Salidas estructuradas: `src/agents/schemas.py`
- Sin gating por fase: `src/agents/guardrails.py`

### Persistencia y firma operativa (plan Fase B)
- Postgres + pgvector: `src/storage/sql.py`, `deploy/docker-compose.yml`, `render.yaml`
- Migraciones: `0001` + `0002` (sesiones/trazas)
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

### Despliegue
- Producción: `https://agente-de-ia-juridico.onrender.com` — `persistencia: postgres`
- Local: `./scripts/start-local.sh` (Docker + fallback memoria)

## Pendiente prioritario (siguiente sprint)

### P0 — Operación despacho
1. **Configurar Slack en Render** (`SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, canal revisión) y probar HITL end-to-end.
2. **Checklist REQ-001…050** — marcar `activo` + prueba manual por requisito en `requisitos_asistente.json`.
3. **Tutela completa (REQ-038…042)** — borrador estructurado `output_type=Tutela` + término 10 días al aprobar (parcial hoy).

### P1 — Continuidad y datos
4. **UI carga historial servidor** — consumir `GET /chat/history` al abrir chat (hoy solo localStorage).
5. **Ingesta expediente desde adjuntos** en flujo chat (API existe en firma_api).
6. **Extracción expediente con LLM** opcional cuando heurísticas no alcanzan (sin inventar).

### P2 — Fase 2 original (gestión procesal)
7. REQ-043…047 — seguimiento radicaciones, informes mensuales (agente `dependiente_judicial` + integraciones externas).
8. REQ-041 — seguimiento radicación tutela en línea (integración manual o scraping — no automatizar sin fuente oficial).

### P3 — Canales
9. **WhatsApp** — reglas globales lo listan; plan lo retiró. Decisión pendiente: reintroducir `src/channels/whatsapp` o actualizar reglas a solo Slack+web.

## Documentos históricos (no borrar, contexto)

| Archivo | Estado |
|---------|--------|
| `agente/fases/FASE_0.md` | Cerrada — `ACTA_CIERRE_FASE_0.md` |
| `agente/fases/FASE_1.md` | **Obsoleta** (gating); capacidades viven en firma |
| `agente/fases/FASE_2.md` | Stub roadmap |
| `agente/fases/FASE_3.md` | Stub roadmap; tutelas/conceptos ya en agentes |
| `docs/canon/plan-rediseno-firma.md` | Plan maestro técnico |

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

# Roadmap — Plan de ejecución agente-usuario

> **Fase actual: 3 completada** · plantillas, dashboard audit portal, export MD · **Fase 3.5 en dev:** contexto auditable por guía

## Fase 3.5 — Contexto auditable por guía (dev)

- Portal: instrucción tipo, herramientas y guardrails del skill como ítems Aprobar/Ajustar (bucket `guias`)
- Catálogo `audit-data.json` v2.1 con `tools`, `guardrails`, `audit_keys`, `source_path`
- Persistencia `legal-audit-sync-v4`
- Plan: [`docs/canon/plan-auditoria-contexto-guias-dev.md`](plan-auditoria-contexto-guias-dev.md)

## Fase 3 — Producto y auditoría — COMPLETADA

- Plantillas por tipo: cronología, tutela, audiencia (`src/agents/plan_templates.py`)
- Recordar patrón por sesión (`src/agents/plan_patterns.py` + checkbox en chat)
- Dashboard portal: `GET /api/audit/execution-plans/dashboard`
- Export MD: `GET /chat/plan/{id}/export.md` y vía API de auditoría
- Plan detallado: [`docs/canon/plan-fase-3-producto-auditoria.md`](plan-fase-3-producto-auditoria.md)

## Fase 1 — Plan + aprobación + ejecución (sin streaming) — COMPLETADA

- Esquemas `ExecutionPlan`, `PlanStep`, `AgentIOReport` en [`src/agents/execution_schemas.py`](src/agents/execution_schemas.py)
- Persistencia Postgres + memoria (`execution_plans`, migración `0005`)
- Endpoints: `POST /chat/plan`, `GET /chat/plan/{id}`, `POST .../approve`, `POST .../reject`
- UI: tarjeta de plan con Aprobar / Solicitar cambios
- Trace v5 con `execution_plan_id`, `plan_steps`, `agent_io_reports`, `user_updates`
- `POST /chat/plan/{id}/approve-and-execute` legacy (síncrono)

## Fase 2 — Updates en vivo — COMPLETADA

### Sprint A (web)
- SSE `GET /chat/plan/{plan_id}/events` con replay y `Last-Event-ID`
- `POST /chat/plan/{plan_id}/execute` (202 async)
- `GET /chat/plan/{plan_id}/result`
- Run Card en chat con estados en tiempo real (`static/chat.js`)
- Heartbeat en broker durante pasos largos
- Reconexión EventSource con backoff

### Sprint B (Slack)
- [`src/channels/slack_plan.py`](src/channels/slack_plan.py): plan en hilo + `EJECUTAR` / `CAMBIOS:`
- Updates por paso en hilo durante ejecución
- `wait_for_plan_completion` para no bloquear 60s

## Fase 3 — Producto y auditoría — COMPLETADA

Ver entregables en [`docs/canon/plan-fase-3-producto-auditoria.md`](plan-fase-3-producto-auditoria.md).

- Plantillas de plan por tipo de consulta (audiencia, tutela, cronología)
- Dashboard en audit portal: planes aprobados vs ejecutados
- Export MD del plan + I/O por caso para trazabilidad del despacho
- Opción «aprobar y recordar patrón» por sesión

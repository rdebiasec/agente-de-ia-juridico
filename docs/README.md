# Documentación — agente penal-víctimas

## Estructura

| Carpeta | Contenido |
|---|---|
| [`canon/`](./canon/) | Fuente viva — editar aquí |
| [`auditoria/`](./auditoria/) | Reportes de pasos por skill; [runbook progreso prod](./auditoria/runbook-progreso-auditoria.md) |
| [`operaciones/`](./operaciones/) | DR / runbooks (p. ej. [plan de desastre](./operaciones/PLAN_DESASTRE.md)) |
| [`entregables/`](./entregables/) | Versiones para abogada y comercial |
| [`generados/`](./generados/) | Volcados automáticos (no editar a mano) |
| [`archive/`](./archive/) | Documentos históricos |
| [`assets/`](./assets/) | Imágenes compartidas |

## Archivos clave

- **Catálogo canónico:** [`canon/lista-aprobacion-agentes-skills-pasos.md`](./canon/lista-aprobacion-agentes-skills-pasos.md)
- **Guía de flujos:** [`canon/guia-aprobacion-abogada-flujos-penal-victimas.md`](./canon/guia-aprobacion-abogada-flujos-penal-victimas.md)
- **Plan firma virtual:** [`canon/plan-rediseno-firma.md`](./canon/plan-rediseno-firma.md)
- **Udemy Agents SDK → producto (tablero L01–L28, orden pedagógico):** [`canon/plan-udemy-agents-sdk-aplicacion.md`](./canon/plan-udemy-agents-sdk-aplicacion.md)
- **Plan corto + Ahora:** [`canon/PLAN_UDEMY_CORTO.md`](./canon/PLAN_UDEMY_CORTO.md)
- **Prompt de clase (educativo):** [`canon/PROMPT_CLASE_UDEMY.md`](./canon/PROMPT_CLASE_UDEMY.md)
- **Cambios Udemy (qué / por qué, L01–L28 en un solo doc):** [`auditoria/UDEMY_LISTA_CAMBIOS.md`](./auditoria/UDEMY_LISTA_CAMBIOS.md)
- **Checklist de cierre por lección:** [`canon/CHECKLIST_UDEMY_CIERRE_LECCION.md`](./canon/CHECKLIST_UDEMY_CIERRE_LECCION.md)
- **Registro vivo de revisiones:** [`canon/REGISTRO_UDEMY_REVISIONES.md`](./canon/REGISTRO_UDEMY_REVISIONES.md)
- **Dashboard:** [`canon/udemy-plan-dashboard.html`](./canon/udemy-plan-dashboard.html)
- **Plantilla auditoría por lección:** [`auditoria/PLANTILLA_udemy-leccion.md`](./auditoria/PLANTILLA_udemy-leccion.md)
- **Flujos SPOA frecuentes (sin handoffs peer):** [`canon/flujos-frecuentes-penal-victimas-co.md`](./canon/flujos-frecuentes-penal-victimas-co.md)
- **Cumplimiento Colombia (Ley 1581):** [`auditoria/reporte-cumplimiento-colombia-2026-07-20.md`](./auditoria/reporte-cumplimiento-colombia-2026-07-20.md)
- **Runbook cumplimiento operativo:** [`operaciones/RUNBOOK_CUMPLIMIENTO_1581.md`](./operaciones/RUNBOOK_CUMPLIMIENTO_1581.md)
- **Forecast $/turno:** [`operaciones/FORECAST_COSTOS_TURNOS.md`](./operaciones/FORECAST_COSTOS_TURNOS.md)
- **Slack HITL Render:** [`operaciones/SLACK_HITL_RENDER.md`](./operaciones/SLACK_HITL_RENDER.md)
- **Plantilla DPA encargados:** [`operaciones/PLANTILLA_DPA_ENCARGADOS.md`](./operaciones/PLANTILLA_DPA_ENCARGADOS.md)
- **Checklist RNBD/SIC:** [`operaciones/CHECKLIST_RNBD_SIC.md`](./operaciones/CHECKLIST_RNBD_SIC.md)
- **Auditoría viva Gerente + agentes (un solo doc):** [`auditoria/AUDITORIA_GERENTE_Y_AGENTES.md`](./auditoria/AUDITORIA_GERENTE_Y_AGENTES.md)
- **Resumen auditoría pasos:** [`auditoria/reporte-ejecutivo-auditoria-pasos-skills.md`](./auditoria/reporte-ejecutivo-auditoria-pasos-skills.md)

## Regenerar

```bash
python scripts/auditar_pasos_skills_gerencia.py --apply --regenerar
python scripts/generar_documento_unico_aprobacion.py
python scripts/generar_audit_portal.py
```

## Portal de auditoría (abogada)

```bash
./scripts/start-audit-portal.sh
```

Abrir `http://localhost:8080` (v2.1).

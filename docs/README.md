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
- **Flujos SPOA frecuentes (sin handoffs peer):** [`canon/flujos-frecuentes-penal-victimas-co.md`](./canon/flujos-frecuentes-penal-victimas-co.md)
- **Cumplimiento Colombia (Ley 1581):** [`auditoria/reporte-cumplimiento-colombia-2026-07-20.md`](./auditoria/reporte-cumplimiento-colombia-2026-07-20.md)
- **Runbook cumplimiento operativo:** [`operaciones/RUNBOOK_CUMPLIMIENTO_1581.md`](./operaciones/RUNBOOK_CUMPLIMIENTO_1581.md)
- **Plantilla DPA encargados:** [`operaciones/PLANTILLA_DPA_ENCARGADOS.md`](./operaciones/PLANTILLA_DPA_ENCARGADOS.md)
- **Checklist RNBD/SIC:** [`operaciones/CHECKLIST_RNBD_SIC.md`](./operaciones/CHECKLIST_RNBD_SIC.md)
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

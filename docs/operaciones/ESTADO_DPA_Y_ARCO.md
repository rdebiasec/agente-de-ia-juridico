# Estado DPA / encargados (operativo)

Checklist vivo. Completar firmas fuera del código; este archivo solo rastrea evidencia.

| Encargado | Estado | Evidencia / dónde | Próxima revisión |
|-----------|--------|-------------------|------------------|
| OpenAI | Pendiente evidencia en despacho | Portal DPA del plan contratado; plantilla [`PLANTILLA_DPA_ENCARGADOS.md`](PLANTILLA_DPA_ENCARGADOS.md) | Trimestral |
| Render | Pendiente evidencia en despacho | DPA Render + Postgres en Oregon | Trimestral |
| Slack | Pendiente si HITL prod activo | Customer DPA Slack | Al activar token |
| Twilio | N/A si no hay SMS | — | — |

**Rotación de cifrado:** `DATA_AT_REST_KEY` debe ser independiente de `SESSION_SECRET` en Render (ya está en `render.yaml`). Si se rota la clave, planificar re-cifrado o aceptar que datos viejos no se lean — documentar el corte en el gestor de secretos.

**ARCO:** chat web autenticado → `POST /api/compliance/arco-erase` (borra historial, trazas, borradores, expediente, planes; conserva consentimientos y access logs). Portal auditoría → «Borrar mi progreso» / correo `privacidad@dbxsolutions.com`.

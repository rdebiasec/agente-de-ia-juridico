# Plantilla / checklist DPA — encargados del tratamiento

**Responsable:** DBX Solutions · `privacidad@dbxsolutions.com`  
**Uso:** archivar PDF firmado (o aceptación electrónica del proveedor) por cada encargado. No sustituye asesoría legal externa.

## Proveedores actuales

| Encargado | Datos que trata | Región típica | Estado DPA (llenar) | Fecha revisión |
|-----------|-----------------|---------------|---------------------|----------------|
| OpenAI | Prompts, respuestas, embeddings de texto de casos | EE.UU. | [ ] Firmado / [ ] Enterprise / [ ] Pendiente | |
| Render | App, logs, Postgres (chat, drafts, traces, consent) | Oregon (EE.UU.) | [ ] Firmado / [ ] Pendiente | |
| Slack | Borradores HITL (texto truncado), metadatos de canal | EE.UU. | [ ] Firmado / [ ] Pendiente | |
| Twilio (si activo) | Texto de alerta de plazos (sin cuerpo de caso) | EE.UU. | [ ] N/A / [ ] Firmado | |

## Cláusulas mínimas a verificar en cada DPA

1. Identificación de responsable vs encargado.
2. Finalidad limitada al servicio contratado.
3. Medidas de seguridad (cifrado en tránsito, control de acceso).
4. Subencargados y notificación de cambios.
5. Transferencias internacionales / cláusulas tipo SCC o equivalente.
6. Asistencia ARCO y notificación de incidentes (plazo).
7. Supresión o devolución al terminar el contrato.
8. Auditoría / informes SOC2 o equivalente (si aplica).

## Enlaces útiles (verificar vigencia)

- OpenAI: portal de privacidad / DPA del plan contratado  
- Render: Data Processing Addendum  
- Slack: Customer Data Processing Addendum  
- SIC Colombia — Ley 1581: https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-1581  

## Cadencia

Revisión trimestral (ver `RUNBOOK_CUMPLIMIENTO_1581.md`). Tras cada cambio de proveedor o región, actualizar aviso `/legal/privacidad` §9.

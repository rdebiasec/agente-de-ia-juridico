# Runbook cumplimiento Ley 1581 / despacho

## Controles técnicos (producto)

| Control | Dónde |
|---------|--------|
| Consentimiento hard en login web | `POST /auth/login` exige `accept_privacy` + `accept_sensitive_data` (HTTP 428 si falta) |
| Consentimiento portal auditoría | HTTP 428 + PIN |
| ARCO chat web | `POST /api/compliance/arco-erase` (sesión autenticada) |
| ARCO portal | «Borrar mi progreso» / `DELETE /api/audit/progress` (archiva snapshot) |
| Retención | Policy 3y auditoría / 5y chat; job mensual scheduler + `scripts/purge_retention.py` |
| Idle UI chat | Default **60 min** (`SESSION_IDLE_MINUTES`) — cierra sesión de navegador; **no** borra historial ni expediente |
| Idle ≠ retención ≠ HITL | Idle no dispara purge. Retención 5y chat / 3y auditoría. **No** borrar expediente/chat si hay borrador HITL pendiente de aprobación |
| Smoke retención | `DATABASE_URL=... python scripts/purge_retention.py --dry-run` (solo cuenta; no borra) |
| Bitácora del caso | `Expediente.bitacora` (notas Gerente + especialistas) — **dato de caso**; mismo consentimiento; se borra con ARCO/`arco-erase` |
| Páginas | `/legal/privacidad`, `/legal/tratamiento-datos-casos`, `/legal/terminos` |
| Front-office `/cliente` (local/dev) | Consentimiento en UI; cookie `lexiatek_cliente_session` **distinta** de `agente_session` del desk; respuestas solo tras HITL del abogado; allowlist no aplica a `/cliente*` |

## Front-office víctima (`/cliente`) — solo local/dev

- **No publicar a prod** sin OK explícito del responsable.
- Identidad víctima: cookie `lexiatek_cliente_session` (no reutilizar sesión del abogado).
- Flujo: mensaje → borrador outbound `proposed` → abogado aprueba → mensaje `client_visible`.
- ARCO: mismo canal de contacto del despacho (`privacidad@…`); borrado fino de hilos cliente se endurece con Fase 5+ cuando haya prod.
- Datos: preferir sintéticos en local; no cargar expedientes reales de víctimas en laptops sin cifrado.

## Encargados / DPA (operación — fuera del código)

Plantilla: [`PLANTILLA_DPA_ENCARGADOS.md`](./PLANTILLA_DPA_ENCARGADOS.md) · RNBD: [`CHECKLIST_RNBD_SIC.md`](./CHECKLIST_RNBD_SIC.md).

Mantener archivo firmado (Drive/legal) para:

1. **OpenAI** — procesamiento de prompts/embeddings (transferencia EE.UU.).
2. **Render** — hosting y Postgres (región documentada en aviso).
3. **Slack** — borradores HITL en canal `#revision-abogado`.

Checklist trimestral: vigencia DPA, lista de subprocesadores, rotación de tokens, revisión de canal Slack (privado, miembros del despacho).

**Google Drive Lexiatek (local/dev):** espejo de `Expediente.bitacora` vía service account + Shared Drive **Lexiatek** (archivos `.md`). Checklist: [`GOOGLE_DRIVE_LEXIATEK.md`](./GOOGLE_DRIVE_LEXIATEK.md).  
**Prod / datos reales:** no activar hasta DPA con Google + aviso/RNBD. En local solo sintéticos/anonimizados.

## Datos reales en local/dev

**Prohibido** cargar expedientes reales de víctimas en:

- entorno con `DEV_AUTO_LOGIN=true`
- `DATABASE_URL` vacío (memoria)
- laptops sin cifrado de disco

Usar datos anonimizados o sintéticos. Prod = única fuente de verdad para casos reales.

## ARCO — procedimiento humano

1. Recibir solicitud en `privacidad@dbxsolutions.com`.
2. Identificar titular (correo portal o usuario web).
3. Portal: pedir «Borrar mi progreso» o ejecutar delete API.
4. Chat: titular autenticado ejecuta `arco-erase`, o soporte borra con `erase_web_subject(user_id)`.
5. Confirmar por correo; conservar evidencia del trámite (no el contenido del caso).

## WhatsApp

Canal **no implementado**. Producción autorizada: **web + Slack**. No activar WhatsApp sin evaluación Ley 1581 + Ley 2300.

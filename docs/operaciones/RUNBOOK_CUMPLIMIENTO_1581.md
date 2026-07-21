# Runbook cumplimiento Ley 1581 / despacho

## Controles técnicos (producto)

| Control | Dónde |
|---------|--------|
| Consentimiento hard en login web | `POST /auth/login` exige `accept_privacy` + `accept_sensitive_data` (HTTP 428 si falta) |
| Consentimiento portal auditoría | HTTP 428 + PIN |
| ARCO chat web | `POST /api/compliance/arco-erase` (sesión autenticada) |
| ARCO portal | «Borrar mi progreso» / `DELETE /api/audit/progress` (archiva snapshot) |
| Retención | Policy 3y auditoría / 5y chat; job mensual scheduler + `scripts/purge_retention.py` |
| Páginas | `/legal/privacidad`, `/legal/tratamiento-datos-casos`, `/legal/terminos` |

## Encargados / DPA (operación — fuera del código)

Plantilla: [`PLANTILLA_DPA_ENCARGADOS.md`](./PLANTILLA_DPA_ENCARGADOS.md) · RNBD: [`CHECKLIST_RNBD_SIC.md`](./CHECKLIST_RNBD_SIC.md).

Mantener archivo firmado (Drive/legal) para:

1. **OpenAI** — procesamiento de prompts/embeddings (transferencia EE.UU.).
2. **Render** — hosting y Postgres (región documentada en aviso).
3. **Slack** — borradores HITL en canal `#revision-abogado`.

Checklist trimestral: vigencia DPA, lista de subprocesadores, rotación de tokens, revisión de canal Slack (privado, miembros del despacho).

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

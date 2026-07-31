# Slack HITL en Render (B12)

## Variables requeridas

| Env | Ejemplo | Notas |
|---|---|---|
| `SLACK_BOT_TOKEN` | `xoxb-…` | Bot del workspace |
| `SLACK_APP_TOKEN` | `xapp-…` | **Socket Mode** (no confundir con bot) |
| `SLACK_SIGNING_SECRET` | secreto app | Interactivity |
| `SLACK_REVIEW_CHANNEL` | `#revision-abogado` | Canal privado del despacho |
| `SLACK_APPROVER_IDS` | `U01…,U02…` | CSV de user IDs autorizados |

Sin `SLACK_APP_TOKEN`, el Socket Mode **no arranca** (warning en logs al boot).

## Verificación

1. Deploy Render con las 3 credenciales + channel + approvers.
2. `GET /health` → `slack_socket_started: true` (o campo equivalente en health).
3. Crear borrador HITL desde web → mensaje en canal con Aprobar / Editar / Rechazar.
4. Solo IDs en `SLACK_APPROVER_IDS` pueden actuar (si la lista no está vacía).

## Smoke local

```bash
# Con tokens en .env
./scripts/start-local.sh
# Opcional:
python scripts/smoke_slack_hitl_drafts.py
```

## Estado

Configuración = **ops** (secretos en Render). Código HITL Slack ya existe (`src/hitl/slack_review.py`, Socket Mode).

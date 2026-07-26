# Smoke del Gerente del Caso Penal — 2026-07-25

Verificación funcional del gate de completitud sobre HTTP autenticado, en local y en producción, tras el deploy del commit `bb82c50`.

Script reutilizable: `scripts/smoke_gerencia_prod.py`

## Resultado

| Check | Local | Producción |
|---|---|---|
| Caso incompleto queda en `awaiting_input` | PASS | PASS |
| Plan incompleto sin especialistas (solo el gerente) | PASS | PASS |
| Reporta los faltantes bloqueantes | PASS | PASS |
| Plan incompleto no se puede aprobar | PASS (HTTP 400) | PASS (HTTP 400) |
| Caso completo llega a `pending_approval` | PASS | PASS |
| Caso completo incluye al especialista | PASS | PASS |

**Resultado: PASS en local y en producción.**

## Evidencia

Con el mensaje de alto riesgo sin datos (`"Redacte un memorial de impulso para la víctima."`):

- Estado: `awaiting_input`
- Pasos: solo `coordinador_expediente_penal`
- Faltantes reportados: `hechos mínimos del caso`
- Aprobación rechazada: `El plan no está pendiente de aprobación (estado: awaiting_input).`

Con radicado, hechos, poder, última actuación y partes, el plan pasa a `pending_approval` e incorpora `redactor_documentos_juridicos_penales` junto a los analistas.

## Ledger persistido en producción

Sesión `web:web-72584a21` en la base activa de Render:

```
faltantes_gerencia: []
tareas_gerencia: [ { titulo: "hechos mínimos del caso", estado: "cerrada", responsable: "abogado_titular" } ]
metricas_gerencia: { verificaciones: 2, bloqueos_por_faltantes: 1, verificaciones_aprobadas: 1 }
```

El bloqueo se registró en la primera verificación y la tarea se cerró al llegar el dato, que es exactamente el comportamiento esperado del ledger.

## Otros smokes de este cierre

- Infraestructura (`scripts/smoke_produccion.sh`): PASS, 0 fallos. Reporte en `smoke-produccion-reporte.md`.
- Login del portal de auditoría local y producción (`scripts/smoke_audit_login.py`): PASS en ambos.
- Slack: 6 pruebas verdes, socket activo en producción y `awaiting_input` manejado en `src/channels/slack_plan.py`.
- Migración: esquema en `0008` y columnas del ledger presentes en la base activa.

## Correcciones hechas durante el smoke

Dos checks daban falso FAIL por estar desactualizados, no por fallas del producto:

- `smoke_produccion.sh` buscaba el texto «10 reglas estrictas», que ya no existe desde el rediseño del portal como editor por agente. Ahora verifica la pestaña de guardrails. También se corrigió un `|| echo 0` que duplicaba el valor y rompía la comparación.
- `smoke_audit_login.py` exigía que la sesión quedara cerrada tras el logout, lo que en local es imposible con `DEV_AUTO_LOGIN` activo. Ahora acepta la reapertura automática solo cuando el servidor reporta ese modo.

## Publicación del prompt en la base viva

El gate es código y funcionó desde el primer intento, pero el **texto** del Gerente vive en el config store, y ahí Postgres es autoritativo. En producción seguía activo el prompt viejo del coordinador (`v1`).

Causa doble: el sync abortaba por un baseline de versión desalineado, y el `DATABASE_URL` del CI apunta a una base distinta de la que lee la aplicación.

Se publicaron el prompt y los tres guardrails en la base viva con `scripts/publicar_config_gerente.py --prod --apply`, quedando en `v2`:

| Item | Antes | Después |
|---|---|---|
| `prompt/coordinador_expediente_penal` | v1, sin el rol de Gerente | v2, con el rol de Gerente |
| `agent_guardrail/...__input` | v1 | v2 |
| `agent_guardrail/...__output` | v1 | v2 |
| `agent_guardrail/...__tools` | v1 | v2 |

El script es idempotente: una segunda corrida reporta `ya_publicado: true` y no crea versiones nuevas. Las versiones quedaron a nombre de la cuenta de smoke; si la autoría importa para la traza, conviene republicar con el correo real.

## Pendiente de clic humano

El smoke de Slack HITL (`scripts/smoke_slack_hitl_drafts.py`) publica borradores reales en `#revision-abogado` y requiere que una persona pulse Aprobar y Rechazar. No se ejecutó para no dejar ruido en el canal del despacho sin autorización previa.

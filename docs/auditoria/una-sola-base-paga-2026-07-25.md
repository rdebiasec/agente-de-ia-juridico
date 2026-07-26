# Una sola base paga — arranque de cero (2026-07-25)

## Qué se hizo

1. Wipe total de `agente-ia-juridico-db` (workflow `Ops wipe public schema`, confirm `WIPE`).
2. `render.yaml` apunta el servicio a `agente-ia-juridico-db` (plan `basic-256mb`) y deja de declarar la gratis.
3. Blueprint sync + deploy live (`dep-d9im3nhbip4c73csn2qg`): migraciones Alembic hasta `0008` y seed del config store desde archivos.
4. Verificado: servicio y CI (`PROD_DATABASE_URL`) escriben en la **misma** base.

## Estado tras el arranque

| Check | Resultado |
|---|---|
| Health | `ok` / `postgres` / `production` |
| Alembic | `0008` |
| Config activa | 145 ítems; prompt del Gerente presente |
| Expedientes migrados de la gratis | 0 (a propósito) |
| Smoke infraestructura | PASS |
| Smoke gerencia | PASS |
| Smoke login auditoría | PASS |

## Mecanismo archivo → base de datos

Editar prompts / guardrails / skills en el filesystem (editor, no el portal):

1. Guardar y hacer commit en `main`.
2. El workflow [`.github/workflows/sync-config.yml`](../../.github/workflows/sync-config.yml) corre automáticamente.
3. Importa el archivo a Postgres (`config_versions` + `config_active`) con autor y nota.
4. Actualiza el header `config-version` en el archivo.

El portal de auditoría sigue siendo otra vía válida (`POST /api/audit/config/save`); ambas escriben en la misma base.

Wipe de emergencia (ops): [`.github/workflows/ops-wipe-schema.yml`](../../.github/workflows/ops-wipe-schema.yml) con input `WIPE`.

## Pendiente humano

Borrar la base gratis huérfana en el dashboard (el API/MCP no la elimina):

https://dashboard.render.com/d/dpg-d9cpmge1a83c739j60dg-a

Nombre: `agente-db`. Ya no está referenciada por el blueprint ni por el servicio.

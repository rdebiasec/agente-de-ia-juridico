# Nota ops — Sync config tras PR #9 (A0–A8)

**Fecha:** 2026-08-06  
**Commit merge análisis:** `036b88f` (PR #9)  
**Run fallido:** https://github.com/rdebiasec/agente-de-ia-juridico/actions/runs/31068465432

## Causa raíz

Tras mergear A0–A8, los archivos en `main` declaraban `config-version` **mayor** que la versión activa en Postgres de producción (p. ej. `prompt/coordinador_caso` archivo v28 · DB v5). El clasificador marcaba `unknown` / «indeterminado (falta baseline de header)» y `--apply` abortaba sin escribir.

## Qué no sirve

`--allow-conflicts` **omite** ítems bloqueados; no publica el contenido del repo. No es la vía para aplicar patches intencionales A0–A8.

## Remediación aplicada

En `src/config_store/sync.py`: si el header del archivo es mayor que la versión activa en DB y el cuerpo difiere, el estado pasa a **`file_ahead`** (GitOps: archivo → DB). Tras `--apply`, `save_version` crea `v_db+1` y reescribe el header.

**Riesgo aceptado (documentado):** ediciones hechas solo en el portal sobre esos ítems, sin baseline de header en el repo, se sobrescriben. Rollback: Historial en `/auditoria/`.

**Fuera de alcance de esta nota:** F4 auth portal, F5 notepads.

## Resultado

- **Sync OK:** https://github.com/rdebiasec/agente-de-ia-juridico/actions/runs/31068829945 (`workflow_dispatch`, `dry_run=false`)
- **Importados a DB:** 109 ítems (prompts/guardrails/skills A0–A8 + resto con drift)
- **Headers:** commit `1ffae57` `chore(config): sincronizar headers de versión [skip-config-sync]`

## Verificación

1. Merge / push de `cursor/fix-sync-config` a `main`.
2. `workflow_dispatch` de Sync config con `dry_run=false` (el push del fix no toca paths de config, no dispara solo).
3. Job verde; headers commiteados con `[skip-config-sync]` si hubo escritura.

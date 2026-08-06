# Runbook — Notepads por especialista (F5 / F-08 / F-13)

Shared Drive Lexiatek: [carpeta raíz](https://drive.google.com/drive/folders/0ABOGkPnKHSC5Uk9PVA) (`FOLDER_ID=0ABOGkPnKHSC5Uk9PVA`).

## Modelo dual

| Capa | Rol | Dónde |
|---|---|---|
| **Autorativo** | Fuente de verdad | Postgres `Expediente.bitacora` (notas Gerente + `notas_trabajo` de especialistas vía `src/services/bitacora.py`) |
| **Plantillas repo** | Contrato MD + secciones | `agente/notepads/_TEMPLATE.md` y `agente/notepads/{agent_id}.md` |
| **Espejo Drive** | Lectura humana / panel | `casos/<session>/bitacora.md` + `casos/<session>/notepads/{agent_id}.md` |

Código:

- Persistencia: `src/services/bitacora.py` (`append_entries`, `extract_and_persist_specialist_output`)
- Render notepad: `src/services/notepads.py`
- Sync Drive: `src/services/drive_bitacora.py` (`sync_expediente_bitacora` → también `sync_expediente_notepads`)

## Cómo escriben notas los agentes

1. El especialista emite salida estructurada con `notas_trabajo[]` (`NotaTrabajo` en `src/agents/schemas.py`).
2. El runner/post-hook llama `extract_and_persist_specialist_output(session_id, agent_id, output)`.
3. Las notas se normalizan y se appenden a `Expediente.bitacora` (autor = `agent_id`).
4. Tras el append, `sync_expediente_bitacora` (best-effort) reescribe:
   - `bitacora.md` (maestra Gerente)
   - `notepads/{agent_id}.md` para los 10 especialistas canónicos (filtrando por autor)

Prompts: sección `## notas_especialista` en `agente/prompts/agents/*.md`.

## Contrato mínimo de cada notepad

Frontmatter + secciones (plan §4.5):

1. Metadatos (`caso_id`, `agent_id`, `updated_at`, `eval_or_session`)
2. Hechos usados (con fuente)
3. Inferencias (separadas)
4. Pendientes `[PENDIENTE DE VERIFICAR]`
5. Citas KB / normas
6. Decisiones HITL
7. Próxima pregunta al Gerente / abogado
8. Entradas de bitácora (espejo filtrado)

## Sync / smoke

Prerrequisitos Drive: ver [`GOOGLE_DRIVE_LEXIATEK.md`](./GOOGLE_DRIVE_LEXIATEK.md) (SA + `GOOGLE_DRIVE_*`).

```bash
# Solo plantillas + MD local (sin API)
python scripts/sync_drive_notepads.py --local-only

# Con credenciales (.env): escribe casos/web-_smoke_notepads/notepads/*.md
python scripts/sync_drive_notepads.py

# Un agente
python scripts/sync_drive_notepads.py --agent analista_responsabilidad_tipicidad
```

Si faltan credenciales, el script hace **fallback local** a `tmp/notepads-smoke/` (no falla CI).

Smoke bitácora maestra existente:

```bash
python scripts/smoke_drive_bitacora.py
```

## Cumplimiento 1581

- Solo **sintético/anonimizado** en local hasta DPA Google.
- ARCO borra `Expediente.bitacora` (y progreso); borrado de carpeta Drive = fase 2 (documentado en ops).
- No subir PII real de víctimas a Drive de prueba.

## Estructura Drive objetivo

```text
Lexiatek/   # 0ABOGkPnKHSC5Uk9PVA
  casos/
    <session-sanitizado>/
      bitacora.md
      notepads/
        coordinador_caso.md
        analista_cronologia_hechos.md
        analista_responsabilidad_tipicidad.md
        …
```

Piloto eval: carpetas `casos/eval-<id>/` con los mismos archivos (sin PII).

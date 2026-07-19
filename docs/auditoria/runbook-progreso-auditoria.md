# Runbook — progreso del portal de auditoría (prod)

Operaciones para listar, restaurar y vigilar el progreso por correo.
**No inventar decisiones.** Solo restaurar desde historial Postgres o JSON exportado por la abogada.

## Protecciones ya en producción (`dba3fac`+)

| Capa | Comportamiento |
|------|----------------|
| Cliente | Sync del servidor antes del primer render; `progressUserDirty` (solo PUT tras edición real); `peekDecision` |
| API | `PUT /api/audit/progress` rechaza **regresión** de conteo de decisiones (HTTP **409**); rate limit de PUTs |
| Historial | Hasta ~60 instantáneas; no se poda la mejor con decisiones > 0 |
| Borrado | Solo `DELETE` explícito («Borrar mi progreso») / ARCO |

Acción de log: `put_progress_rejected` con detalle `regression_blocked:N->M`.

## 1. Listar progreso (producción)

Obtener **External Database URL** en Render → Postgres **`agente-db`** → Connect.
Convertir `postgres://` → `postgresql+psycopg://` si hace falta.

```bash
cd "/Users/ricardodebiase/Documents/agente de IA juridico"

DATABASE_URL='postgresql+psycopg://USER:PASS@HOST/DATABASE' \
  .venv/bin/python scripts/restore_audit_progress.py \
  --email michele.aguilar@dbx-solutions.com --list
```

Interpretación:

| Resultado | Acción |
|-----------|--------|
| `decisions > 0` en actual | Progreso vivo; no restaurar |
| Actual `0` / vacío, historial con `decisions > 0` | Candidato a `--restore` |
| Actual e historial en `0` | **No recuperable por DB** — pedir export JSON a la abogada |

## 2. Restaurar desde historial

Solo tras `--list` y confirmación humana. Preferir `--dry-run` si el script lo soporta.

```bash
# Simular (si disponible):
DATABASE_URL='…' .venv/bin/python scripts/restore_audit_progress.py \
  --email michele.aguilar@dbx-solutions.com --restore --dry-run

# Aplicar (elige la instantánea con más decisiones, o --history-id N):
DATABASE_URL='…' .venv/bin/python scripts/restore_audit_progress.py \
  --email michele.aguilar@dbx-solutions.com --restore
```

Luego: la abogada hace login en `/auditoria/`, hard-refresh (Cmd+Shift+R), verifica el contador.

Ver también DR D10 en [`docs/operaciones/PLAN_DESASTRE.md`](../operaciones/PLAN_DESASTRE.md).

## 3. Consulta read-only vía Render MCP

Con [Render MCP](https://render.com/docs/mcp-server) configurado en Cursor (`~/.cursor/mcp.json`) y workspace **DBX Solutions**:

1. `list_postgres_instances` → id de `agente-db` (p. ej. `dpg-…`).
2. `query_render_postgres` (solo lectura), ejemplos:

```sql
-- Fila actual
SELECT email, updated_at, payload->>'savedAt' AS saved_at
FROM audit_portal_progress
WHERE email = 'michele.aguilar@dbx-solutions.com';

-- Historial reciente
SELECT id, created_at, payload->>'savedAt' AS saved_at
FROM audit_portal_progress_history
WHERE email = 'michele.aguilar@dbx-solutions.com'
ORDER BY created_at DESC
LIMIT 30;

-- Rechazos de PUT (regresión bloqueada)
SELECT created_at, action, detail
FROM audit_portal_access_log
WHERE email = 'michele.aguilar@dbx-solutions.com'
  AND action = 'put_progress_rejected'
ORDER BY created_at DESC
LIMIT 20;
```

MCP **no escribe**. Para restaurar usar `scripts/restore_audit_progress.py`.

## 4. Monitoreo: `put_progress_rejected`

Si aparece en `audit_portal_access_log`, el servidor **protegió** datos: un cliente intentó bajar el conteo de decisiones.

- Un caso aislado: normal (pestaña vieja / race); el portal debe resincronizar.
- Pico repetido: revisar versión de `app.js` en prod y que no haya caché antigua.

## 5. Rotación de API key de Render (obligatorio si se filtró)

Si una key `rnd_…` se pegó en chat o logs:

1. [dashboard.render.com](https://dashboard.render.com) → Account Settings → API Keys → **revoke** la comprometida.
2. Crear una nueva key.
3. Actualizar solo `~/.cursor/mcp.json` (permisos `600`); **nunca** commit al repo.
4. Reiniciar Cursor / recargar MCP.
5. Probar: list workspaces / list Postgres.

## 6. Backup humano (abogadas)

En el portal: **Exportar progreso JSON** de forma periódica (p. ej. semanal o al cerrar sesión de revisión larga).
Ese archivo es la vía de recuperación si el historial DB no tiene decisiones.

### Mensaje sugerido a Michele (si pierde progreso)

> Tu cuenta (`michele.aguilar@dbx-solutions.com`) está activa. Hubo un fallo técnico (ya corregido) que pudo vaciar el progreso en el servidor; el historial que quedó en Postgres no tiene decisiones recuperables. Si exportaste un JSON desde «Exportar progreso», envíalo y lo reimportamos. Si no, hay que rehacer la revisión; el sistema ya bloquea que un navegador vuelva a sobrescribir trabajo con un estado vacío o peor.

## 7. Caso Michele (referencia, 2026-07)

Consultado en prod vía Render MCP:

- Fila en `audit_portal_progress` con ~693 ítems en `PENDIENTE` → **0** APROBADO/AJUSTAR.
- Últimas 30 filas de historial también en 0 decisiones → **`--restore` no aporta**.
- Recuperación: solo export JSON de la abogada, si existe.

## Checklist rápido

- [ ] `--list` en prod antes de cualquier `--restore`
- [ ] No inventar APROBADO/AJUSTAR
- [ ] Tras restore: hard-refresh + verificar contador
- [ ] Rotar API key si se expuso
- [ ] Recordar export JSON a revisores

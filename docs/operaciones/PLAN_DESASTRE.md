# Plan de desastre — stack completo

Recuperación ante fallos de **Mac local**, **Render** y **GitHub Pages**.  
Scripts: [`scripts/dr/`](../../scripts/dr/). Despliegue diario: [`DEPLOY.md`](../../DEPLOY.md).

---

## Resumen ejecutivo

| Prioridad | Qué respaldar | Dónde | Cómo |
|-----------|---------------|-------|------|
| 1 | Código | GitHub `main` | `git push` frecuente |
| 2 | Secretos (`.env`, Render env) | Gestor / Render dashboard | Nunca en git; inventario con `env_inventory.sh` |
| 3 | Postgres (local + prod) | `~/Backups/agente-juridico/postgres/` | `./scripts/dr/backup_postgres.sh` |
| 4 | Progreso auditoría | Mismo Postgres + historial | `restore_audit_progress.py` (punto fino) |

**Orden de recuperación típico (Mac desde cero):**  
clone → `.env` → `rebuild_local.sh` → `restore_postgres.sh` (si hay dump) → `verify_recovery.sh --local`.

**Backups:** fuera del repo, p. ej. `~/Backups/agente-juridico/` (FileVault en Mac).  
**Nunca** commitear `.env`, `*.dump` ni exports con datos de casos.

**Render free:** `agente-db` no tiene PITR ni backups automáticos. El DR de prod depende de `pg_dump` manual.

---

## Inventario de componentes

```mermaid
flowchart TB
  subgraph local [Mac local]
    Mac[Mac + Docker Desktop]
    Venv[.venv Python]
    EnvFile[.env secretos]
    App[FastAPI :8000]
    PGlocal[(Postgres pgvector)]
    Dist[audit-portal/dist]
  end

  subgraph git [GitHub]
    Repo[main codigo]
    GhPages[gh-pages]
  end

  subgraph render [Render]
    Web[agente-de-ia-juridico]
    PGprod[(agente-db)]
  end

  subgraph external [Externos]
    OpenAI[OpenAI]
    Slack[Slack HITL]
    Twilio[Twilio SMS]
  end

  Mac --> Venv --> App
  EnvFile --> App
  App --> PGlocal
  Repo -->|push| Web
  Repo -->|workflow| GhPages
  Web --> PGprod
  GhPages -->|CORS API| Web
  App --> OpenAI
  Web --> OpenAI
  Web --> Slack
  Web --> Twilio
```

| Componente | Dónde | En git | Criticidad | RPO | RTO |
|---|---|---|---|---|---|
| Código | GitHub `main` | Sí | Alta | 0 | 15–30 min |
| Secretos | Mac + Render | **No** | Crítica | Manual | 30–60 min |
| Postgres local | Docker `deploy_pgdata` | No | Media | 24 h | 30–60 min |
| Postgres prod | Render `agente-db` | No | Alta | 24 h | 1–2 h |
| RAG (`document_chunks`) | Postgres | No | Baja | N/A | 15 min (`ingest_kb`) |
| `audit-portal/dist` | Generado | No | Baja | N/A | 2 min |
| Progreso auditoría | Postgres | No | Alta | 24 h | 15 min |
| gh-pages | Rama GitHub | Sí | Media | 0 | 10 min |
| OpenAI / Slack / Twilio | Proveedores | Creds en env | Media | N/A | 15 min |
| Redis | Solo en `.env.example` | — | No usado | — | — |

---

## Matriz de escenarios (D1–D10)

| # | Desastre | Síntoma | Recuperación |
|---|---|---|---|
| D1 | Mac nueva / disco perdido | Sin `.venv`, `.env`, volume | Runbook A |
| D2 | Docker caído / volume corrupto | App en memoria; `local_db.sh` falla | Runbook B |
| D3 | `.env` perdido | Login / OpenAI fallan | Runbook E |
| D4 | Deploy Render roto | `/health` 5xx | Runbook C |
| D5 | Postgres Render vacío/corrupto | Datos perdidos en prod | Runbook C |
| D6 | GitHub Pages desactualizado | UI vieja en Pages | Runbook D |
| D7 | CORS / `AUDIT_API_BASE` mal | Pages sin progreso | Runbook D |
| D8 | OpenAI key revocada | Chat sin respuesta | Runbook E |
| D9 | Rotación `SESSION_SECRET` | Todos deslogueados | Esperado; re-login |
| D10 | Borrado progreso un usuario | Portal vacío | `restore_audit_progress.py` |

---

## Comandos DR

```bash
# Backup local (Docker db corriendo)
./scripts/dr/backup_postgres.sh

# Backup prod (External Database URL desde Render → agente-db)
DATABASE_URL='postgresql://agente:...@dpg-....render.com/agente' \
  ./scripts/dr/backup_postgres.sh --label prod

# Restore local
./scripts/dr/restore_postgres.sh ~/Backups/agente-juridico/postgres/agente-YYYYMMDD-HHMM.dump

# Inventario de secretos (nunca imprime valores)
./scripts/dr/env_inventory.sh

# Reconstruir entorno local
./scripts/dr/rebuild_local.sh

# Verificar
./scripts/dr/verify_recovery.sh --local
./scripts/dr/verify_recovery.sh --prod
```

---

## Runbook A — Reconstruir Mac desde cero (D1)

1. Clonar: `git clone https://github.com/rdebiasec/agente-de-ia-juridico.git`
2. `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
3. Recrear `.env` desde [`.env.example`](../../.env.example) + secretos (gestor o export Render)
4. `./scripts/dr/rebuild_local.sh`
5. Si hay dump: `./scripts/dr/restore_postgres.sh <archivo.dump>`
6. Si no hay dump local pero sí prod: backup prod → restore local
7. `./scripts/dr/verify_recovery.sh --local`
8. Abrir `http://127.0.0.1:8000/auditoria/` — smoke login

---

## Runbook B — Postgres local corrupto (D2)

1. Detener app (`Ctrl+C` en `start-local.sh`)
2. `docker compose -f deploy/docker-compose.yml down`
3. **Con dump:** `./scripts/dr/restore_postgres.sh <dump>` (levanta db si hace falta)
4. **Sin dump:** `docker compose -f deploy/docker-compose.yml down -v` → `./scripts/local_db.sh --ingest`
5. `./scripts/dr/verify_recovery.sh --local`

**Nunca** aplicar `down -v` contra Render.

---

## Runbook C — Recuperar Render (D4 / D5)

1. Dashboard Render → logs del deploy fallido
2. Código malo: `git revert` + push, o Manual Deploy de un commit estable
3. DB: si aún responde, `DATABASE_URL=<External> ./scripts/dr/backup_postgres.sh --label prod` **antes** de tocar; si no, restore del último dump prod (psql/`pg_restore` contra External URL — ver `restore_postgres.sh --remote`)
4. Env críticos: `SITE_PASSWORD` (hash), `SESSION_SECRET`, `DEV_AUTO_LOGIN=false`, `OPENAI_API_KEY`, `DATABASE_URL`
5. `curl https://agente-de-ia-juridico.onrender.com/health` → `persistencia=postgres`
6. `./scripts/dr/verify_recovery.sh --prod`

---

## Runbook D — GitHub Pages roto (D6 / D7)

1. GitHub Actions → «Deploy Legal Audit Portal» → Re-run
2. Si el workflow falla:  
   `AUDIT_API_BASE=https://agente-de-ia-juridico.onrender.com python scripts/generar_audit_portal.py`  
   y publicar `audit-portal/dist` a `gh-pages` (solo emergencia)
3. Confirmar `audit-api-config.js` apunta a Render
4. `./scripts/smoke_produccion.sh` → CORS + `AUDIT_API_BASE` PASS

---

## Runbook E — Pérdida de secretos (D3 / D8)

1. `./scripts/dr/env_inventory.sh` — ver SET / EMPTY / MISSING
2. OpenAI: nueva key → `.env` + Render → restart
3. `SITE_PASSWORD`: `scripts/hash_site_password.py` → mismo hash en local y Render
4. `SESSION_SECRET`: generar nuevo → invalida sesiones (avisar usuarios)
5. Twilio/Slack: copiar desde dashboards respectivos  
   Ver rotación en [`DEPLOY.md`](../../DEPLOY.md) (sección seguridad).

---

## D10 — Restaurar progreso de un usuario

```bash
DATABASE_URL='...' .venv/bin/python scripts/restore_audit_progress.py \
  --email usuario@ejemplo.com --list

# Ver qué se restauraría sin escribir:
DATABASE_URL='...' .venv/bin/python scripts/restore_audit_progress.py \
  --email usuario@ejemplo.com --restore --dry-run

DATABASE_URL='...' .venv/bin/python scripts/restore_audit_progress.py \
  --email usuario@ejemplo.com --restore
```

---

## Política de respaldo (obligatoria)

| Qué | Frecuencia | Destino |
|---|---|---|
| Postgres prod + progreso auditoría | **Diario** (GitHub Actions) | Cloudflare R2 (cifrado GPG) |
| Inventario env | Mensual | `~/Backups/agente-juridico/env-inventory-*.txt` |
| Código | Cada feature | GitHub |
| Dump local (opcional) | Antes de `down -v` | `~/Backups/agente-juridico/postgres/` |

### Backup automático (GitHub Actions → R2)

Workflow: [`.github/workflows/backup-postgres.yml`](../../.github/workflows/backup-postgres.yml)  
Script: [`scripts/dr/backup_to_r2.sh`](../../scripts/dr/backup_to_r2.sh)

**Secrets** (GitHub → Settings → Secrets and variables → Actions):

| Secret | Origen |
|--------|--------|
| `PROD_DATABASE_URL` | Render → `agente-db` → Connections → External Database URL |
| `BACKUP_ENCRYPTION_KEY` | Passphrase GPG (generada una vez) |
| `R2_ACCOUNT_ID` | Cloudflare R2 |
| `R2_ACCESS_KEY_ID` | Token R2 |
| `R2_SECRET_ACCESS_KEY` | Token R2 |
| `R2_BUCKET` | Nombre del bucket (ej. `agente-ia-juridico-backups`) |

**Probar:** Actions → **Backup Postgres → R2** → Run workflow.

**Restaurar desde R2:**

```bash
# Descargar .dump.gpg desde el bucket, luego:
gpg --batch --passphrase "$BACKUP_ENCRYPTION_KEY" -d agente-….dump.gpg > agente.dump
./scripts/dr/restore_postgres.sh agente.dump
# Prod (peligroso): confirmación RESTORE PRODUCTION
# ./scripts/dr/restore_postgres.sh --remote agente.dump
```

Fallback offline (Mac, opcional): `./scripts/dr/daily_backup.sh`

**Reglas anti-pérdida del portal de auditoría**

1. El PUT fusiona; no puede bajar decisiones (APROBADO/AJUSTAR).
2. Logout **no** borra la caché local (va por correo).
3. Sync servidor↔navegador elige/fusiona el lado con más decisiones.
4. Historial Postgres **nunca** poda filas con decisiones.
5. «Borrar mi progreso» archiva en historial antes de borrar.
6. Restore remoto exige escribir `RESTORE PRODUCTION` (no solo `YES`).

---

## Checklist post-recuperación

**Local**

- [ ] `curl http://127.0.0.1:8000/health` → `persistencia: postgres`, `environment: development`
- [ ] Login auditoría: gate se oculta tras correo + `SITE_PASSWORD`
- [ ] `.venv/bin/python -m pytest tests/test_auth.py tests/test_security.py tests/test_prod_followups.py -q`

**Producción**

- [ ] `./scripts/smoke_produccion.sh` → PASS
- [ ] `/health` → `web_auth_enabled: true`, `dev_auto_login: false`
- [ ] Bad login → 401

---

## Fuera de alcance

- Redis multi-instancia
- WhatsApp
- Backups nativos de Render (plan de pago; en free usamos Actions → R2)

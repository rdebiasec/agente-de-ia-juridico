# Despliegue: Mac → GitHub → Render

## Flujo diario

```mermaid
flowchart LR
  Mac[Mac + Cursor]
  GitHub[GitHub agente-de-ia-juridico]
  Render[Render.com]

  Mac -->|git push| GitHub
  GitHub -->|auto deploy| Render
```

1. Desarrollas y pruebas en la Mac
2. `git push` sube cambios a GitHub
3. Render redeploya automáticamente (2–5 min)

---

## Desarrollo local (Mac)

```bash
cd "/Users/ricardodebiase/Documents/agente de IA juridico"
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env   # editar con tus claves

.venv/bin/python scripts/validate_fase0.py
.venv/bin/python -m pytest tests/ -v
.venv/bin/python -m src.main

# Validación extensa (skills + gates + pytest + runtime + smoke HTTP local):
./scripts/validacion_sistema_completa.sh
# Reporte: docs/auditoria/validacion-sistema-completa-reporte.md

# otra terminal:
curl http://localhost:8000/health
```

---

## Subir cambios a GitHub

### Primera vez (crear repo)

```bash
gh auth login          # solo una vez — sigue las instrucciones en pantalla
./scripts/setup-github.sh
```

Eso crea **`agente-de-ia-juridico`** en tu cuenta GitHub (privado) y hace push.

### Día a día

```bash
git add .
git commit -m "Describe tu cambio"
git push origin main
```

**Nunca** subas `.env` — solo `.env.example` sin secretos.

---

## Render (primera vez)

1. Entra en [render.com](https://render.com) → **Sign in with GitHub**
2. **New → Blueprint** (o Web Service)
3. Conecta el repo **`agente-de-ia-juridico`**
4. Render detecta `render.yaml` en la raíz
5. En **Environment**, añade secretos para Fase 0:
   - `OPENAI_API_KEY` (obligatorio para GPT)
   - `SITE_USERNAME`, `SITE_PASSWORD`, `SESSION_SECRET` (login web Fase 0)
   - `SESSION_IDLE_MINUTES=30`
   - `SESSION_COOKIE_SECURE=true` (solo producción HTTPS)
   - `OPENAI_MODEL=gpt-4o-mini`
6. Deploy → URL: `https://agente-de-ia-juridico.onrender.com` (o similar)

### Probar en Render

```bash
curl https://TU-APP.onrender.com/health
curl -X POST https://TU-APP.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Qué áreas del derecho maneja el despacho?"}'
```

En producción, `GET /health` debe mostrar `"web_auth_enabled": true` para que
el flujo de login/logout sea idéntico al local.

`/health` también reporta:

- `"modo": "firma"`
- `"persistencia": "postgres"` cuando `DATABASE_URL` está configurado (Render/Docker), o `"memoria"` en local sin base de datos.
- `"slack_configured"`: `true` solo si se cargan los secretos de Slack para HITL.
- `"twilio_configured"`: `true` solo si hay credenciales Twilio + número destino (`TWILIO_ALERT_TO`).
- `"environment"`: `production` en Render; `development` en local.
- `"dev_auto_login"`: debe ser `false` en producción.

## Seguridad en producción (checklist obligatorio)

Antes del primer deploy en Render, confirme:

| Control | Render / prod | Local dev |
|--------|----------------|-----------|
| `SITE_PASSWORD` | ≥12 chars en claro **o** hash `pbkdf2_sha256$…` (`scripts/hash_site_password.py`) | `.env` local |
| `SESSION_SECRET` | Aleatorio (≥32 chars) | `.env` local |
| `DEV_AUTO_LOGIN` | **`false`** | `true` opcional |
| `APP_DEBUG` | **`false`** (telemetría `/debug/client-log` eliminada del código) | n/a |
| `SESSION_COOKIE_SECURE` | **`true`** | `false` |
| `OPENAI_API_KEY` | Obligatorio | `.env` |
| `DATABASE_URL` | Inyectado por blueprint | Docker local |
| Twilio (opcional) | `TWILIO_*`; callback `POST /twilio/sms-status` | `.env` |

La app **falla al arrancar** en Render si detecta secretos débiles, `DEV_AUTO_LOGIN=true`,
`APP_DEBUG=true`, o falta `OPENAI_API_KEY` / `DATABASE_URL`.

Login web y portal de auditoría tienen **rate limiting**. Slack y Twilio validan firma
en sus webhooks. `/debug/trace/{session_id}` sigue protegido por login web.

Hash recomendado para `SITE_PASSWORD` (paridad local/Render):

```bash
.venv/bin/python scripts/hash_site_password.py 'tu-secreto-largo'
# pegar la salida completa como SITE_PASSWORD en .env y en Render
```

Si `TWILIO_STATUS_CALLBACK` está vacío y existe `RENDER_EXTERNAL_URL`, se usa
`https://…/twilio/sms-status` automáticamente.

Headers de seguridad (HSTS, X-Frame-Options, nosniff, **Content-Security-Policy**) se aplican automáticamente en Render.

### Postgres local (Docker)

El servicio `db` en `deploy/docker-compose.yml` publica el puerto **solo en localhost** (`127.0.0.1:5432`). Las credenciales `agente:agente` son **solo para desarrollo**; no las reutilice en staging ni producción.

### Rate limiting y workers

Los límites de intentos (login web, portal de auditoría, creación/ejecución de planes) viven **en memoria del proceso**. En Render use **un worker por instancia** (configuración actual). Si despliega varias instancias o workers, los límites no se comparten — requerirá Redis u otro almacén compartido (futuro).

Límites actuales (por defecto):

| Ruta | Política |
|---|---|
| `POST /auth/login` | 12 intentos / 15 min por IP |
| `POST /chat/plan` | 20 solicitudes / 15 min por sesión (`subject_id`) |
| `POST /chat/plan/{id}/execute` | 20 ejecuciones / 15 min por sesión |

### CORS (portal GitHub Pages)

Orígenes permitidos por defecto: GitHub Pages (`rdebiasec.github.io`), `localhost:8080`, y la URL pública de Render (`RENDER_EXTERNAL_URL`).

Para añadir orígenes: variable `AUDIT_CORS_ORIGINS` (lista separada por comas). Ejemplo:

```bash
AUDIT_CORS_ORIGINS=https://mi-org.github.io,https://agente-de-ia-juridico.onrender.com
```

Headers permitidos: `Content-Type`, `Authorization`, `Last-Event-ID`.

### Política de rotación de secretos

| Secreto | Cuándo rotar | Efecto |
|---|---|---|
| `SITE_PASSWORD` | Cada 3–6 meses o si hubo filtración | Invalida login del despacho hasta actualizar `.env`/Render |
| `SESSION_SECRET` | Cada 3–6 meses o ante sospecha de compromiso | **Revoca todas las sesiones** web y auditoría |
| `OPENAI_API_KEY` | Si se expuso en logs o commits | Revocar en OpenAI y actualizar Render |

Buenas prácticas:

- No reutilice valores de ejemplo (`Kx9mP2vL8nQw4RsT`, `changeme`, etc.).
- Use `SITE_PASSWORD` de **≥16 caracteres** (recomendado); la app advierte en producción si es más corto.
- Tras rotar `SESSION_SECRET`, todos los usuarios deben volver a iniciar sesión.

**Nunca** suba `.env` a GitHub — solo `.env.example` con placeholders.

## Persistencia y Slack (Fase B)

- `render.yaml` provisiona una base de datos administrada `agente-db` e inyecta `DATABASE_URL`.
- El esquema se gestiona con **Alembic**: al arrancar con `DATABASE_URL`, la app ejecuta
  `alembic upgrade head` (migración inicial: extensión `vector` + tablas `drafts`, `expedientes`,
  `deadlines`, `document_chunks`). Si Alembic falla, hay fallback a `create_all`.
  - Migración manual (opcional): `DATABASE_URL=... .venv/bin/alembic upgrade head`.
- Para habilitar la aprobación desde Slack, configure `SLACK_BOT_TOKEN` y `SLACK_SIGNING_SECRET`
  (secretos `sync:false`) y apunte la URL de interactividad a `POST /slack/interactivity`.
- **Scheduler de plazos**: arranca con la app (APScheduler). Job diario que marca términos
  vencidos y avisa por Slack los próximos a vencer, más un recordatorio mensual de seguimiento.
- **PDF**: el `Dockerfile` ya incluye las libs de WeasyPrint (pango/cairo/gdk-pixbuf), por lo que
  `GET /drafts/{id}/pdf` funciona en Render/Docker sin pasos extra.

### RAG (pgvector)

- La extensión `vector` se crea automáticamente al primer uso del repositorio.
- Tras el primer deploy (o tras cambiar la KB), indexe el conocimiento:

```bash
# Local con Docker:
DATABASE_URL=postgresql+psycopg://agente:agente@localhost:5432/agente \
  .venv/bin/python scripts/ingest_kb.py
# o vía API autenticada:
curl -X POST https://TU-APP.onrender.com/rag/ingest-kb
```

- Requiere `OPENAI_API_KEY` y `EMBEDDING_MODEL` para embeddings reales (sin clave usa un
  embedding local determinista, solo apto para pruebas).

---

## Checklist post-deploy (Fase 0)

```bash
curl https://TU-APP.onrender.com/health
curl https://TU-APP.onrender.com/auth/status
curl -I https://TU-APP.onrender.com/
curl -I https://TU-APP.onrender.com/login
```

Resultados esperados:
- `/health` con `status=ok`, `modo=firma`, `web_auth_enabled=true`
- `/` redirige a login cuando no hay sesión
- `/login` disponible
- `persistencia=postgres` cuando hay `DATABASE_URL`

---

## Plan gratis Render

- El servicio se **duerme** tras ~15 min sin uso
- El primer request puede tardar 30–60 s (cold start)
- Suficiente para desarrollo/staging

---

## Plan de ejecución (Fase 1 + Fase 2 SSE)

El chat web usa **plan obligatorio** antes de ejecutar agentes:

| Endpoint | Uso |
|---|---|
| `POST /chat/plan` | Genera plan (`pending_approval`) |
| `POST /chat/plan/{id}/approve` | Aprueba plan |
| `POST /chat/plan/{id}/reject` | Rechaza con motivo |
| `POST /chat/plan/{id}/execute` | Inicia ejecución async (`202`) |
| `GET /chat/plan/{id}/events` | SSE — avances en vivo |
| `GET /chat/plan/{id}/result` | Resultado final persistido |
| `POST /chat/plan/{id}/approve-and-execute` | Legacy síncrono (tests/compat) |

Persistencia: tabla `execution_plans` (migración Alembic `0005`). Tras deploy, verificar `alembic upgrade head`.

**SSE en Render:** el endpoint envía `heartbeat` cada ~5 s durante pasos largos. Un solo worker por instancia (broker in-process). Multi-instancia requeriría Redis (futuro).

**Slack:** el bot publica el plan en hilo; el usuario responde `EJECUTAR` o `CAMBIOS: motivo`.

**Fase 3:** plantillas de plan, dashboard en `/auditoria/`, export `.md` — ver `docs/canon/plan-fase-3-producto-auditoria.md`.

---

## Portal de auditoría (Auditoría de Instrucciones)

El progreso de aprobación se persiste en **PostgreSQL** por correo electrónico (misma base que el agente).

| Recurso | URL |
|---|---|
| Agente (chat, HITL) | `https://agente-de-ia-juridico.onrender.com` |
| Portal (recomendado, mismo origen) | `https://agente-de-ia-juridico.onrender.com/auditoria/` |
| Portal espejo (GitHub Pages) | `https://rdebiasec.github.io/agente-de-ia-juridico/` |

### Login

- **Correo** — identifica el progreso guardado (normalizado a minúsculas).
- **Contraseña** — misma `SITE_PASSWORD` que el chat del despacho.

### API (`/api/audit`)

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/audit/login` | `{ email, password }` → cookie `audit_session` |
| GET | `/api/audit/session` | `{ authenticated, email }` |
| GET/PUT/DELETE | `/api/audit/progress` | Cargar / guardar / borrar progreso del correo autenticado |

### Cumplimiento y datos de casos (Ley 1581 / US safeguards)

**Sí puede ingresar información de casos** si cumple:

1. Acepta el [aviso de privacidad](/legal/privacidad) y la [autorización de datos de casos](/legal/tratamiento-datos-casos) en el login.
2. Usa **PIN personal** (6–8 dígitos) en el portal de auditoría, además de `SITE_PASSWORD`.
3. Aplica **minimización**: solo datos necesarios para la tarea.

Controles técnicos: consentimiento registrado en Postgres, logs de acceso, historial de versiones del progreso, rate limiting en login, ARCO vía `privacidad@dbxsolutions.com` o «Borrar mi progreso».

Páginas legales públicas: `/legal/privacidad`, `/legal/tratamiento-datos-casos`.

### Paridad dev ↔ prod

| Aspecto | Local (`./scripts/start-local.sh`) | Producción (Render) |
|---|---|---|
| URL portal | `http://127.0.0.1:8000/auditoria/` | `https://agente-de-ia-juridico.onrender.com/auditoria/` |
| `AUDIT_API_BASE` en build | `""` (mismo origen) | `""` (mismo origen, en Dockerfile) |
| Login auditoría | correo + `SITE_PASSWORD` | correo + `SITE_PASSWORD` |
| Persistencia | Postgres si `DATABASE_URL` en `.env` | Postgres (`agente-db`) |
| Chat auto-login | `DEV_AUTO_LOGIN=true` en `.env` | `false` en `render.yaml` |
| Cookie segura | `SESSION_COOKIE_SECURE=false` | `true` |

**Espejo GitHub Pages** (`AUDIT_API_BASE` → Render): mismo login y datos si usan el mismo correo; requiere CORS (ya configurado).

**Preview :8080** (`./scripts/start-audit-portal.sh`): solo para probar cross-origin; no es paridad 1:1 con prod.

Migración: `migrations/versions/0003_audit_portal_progress.py` (aplicada al arrancar con Postgres).

### Desarrollo local

```bash
# App + Postgres
./scripts/start-local.sh

# Build portal (mismo origen en :8000/auditoria)
AUDIT_API_BASE="" python scripts/generar_audit_portal.py

# Abrir http://127.0.0.1:8000/auditoria/
```

Preview estático en `:8080` (API en `:8000`):

```bash
AUDIT_API_BASE=http://127.0.0.1:8000 ./scripts/start-audit-portal.sh
```

### Estructura

```
audit-portal/
  site/     # Fuente HTML/JS
  dist/     # Generado (gitignored); Docker y /auditoria en Render
```

```bash
python scripts/generar_audit_portal.py
```

Variables de build:

- `AUDIT_API_BASE=""` — mismo origen (Render `/auditoria`).
- `AUDIT_API_BASE=https://agente-de-ia-juridico.onrender.com` — GitHub Pages u otro host estático.

CORS (solo si el portal no está en el mismo dominio): `AUDIT_CORS_ORIGINS` (por defecto incluye GitHub Pages y `localhost:8080`).

### GitHub Pages (espejo opcional)

GitHub Pages **no** corre la app Python. El workflow `deploy-audit-portal.yml` publica `audit-portal/dist` con `AUDIT_API_BASE` apuntando a Render.

1. Repo **público** (Pages gratuito).
2. `git push origin main` → rama `gh-pages`.
3. La abogada puede usar Pages o `/auditoria` en Render; el progreso es el mismo si usa el mismo correo.

El export `.md` sigue siendo el dictamen formal al despacho. Respaldo JSON es copia de seguridad adicional.

---

## GitHub Pages (legacy — ver sección anterior)

<details>
<summary>Notas históricas del portal estático</summary>

Portal v2.2: manual de uso en sección 0, audita reglas estrictas, agentes y **cada paso** de cada skill (totales dinámicos).

</details>

---

## Plan de desastre

Runbooks y backups: [`docs/operaciones/PLAN_DESASTRE.md`](docs/operaciones/PLAN_DESASTRE.md).

### Backup / recuperación completa (prod → Cloudflare R2)

- **Backup diario:** Actions → **Backup Postgres → R2** (dump + auditoría + `secrets.env` cifrado).
- **Recuperar:** Actions → **Recover from R2** → descargar artifact → seguir `NEXT_STEPS.txt`.
- Detalle: [`docs/operaciones/PLAN_DESASTRE.md`](docs/operaciones/PLAN_DESASTRE.md).

Secrets mínimos R2: `PROD_DATABASE_URL`, `BACKUP_ENCRYPTION_KEY`, `R2_*`.  
Además, para que el paquete de secretos esté completo: `SITE_PASSWORD`, `SESSION_SECRET`, `OPENAI_API_KEY`, Slack/Twilio si aplica.

```bash
# Backup / restore local (opcional, Docker)
./scripts/dr/backup_postgres.sh
./scripts/dr/restore_postgres.sh ~/Backups/agente-juridico/postgres/agente-….dump
./scripts/dr/verify_recovery.sh --local
./scripts/dr/verify_recovery.sh --prod
```

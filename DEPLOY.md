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
| `SITE_PASSWORD` | Secreto fuerte (≥12 chars), único | `.env` local |
| `SESSION_SECRET` | Aleatorio (≥32 chars) | `.env` local |
| `DEV_AUTO_LOGIN` | **`false`** | `true` opcional |
| `APP_DEBUG` | **`false`** | `false` (o `true` solo al depurar) |
| `SESSION_COOKIE_SECURE` | **`true`** | `false` |
| `OPENAI_API_KEY` | Obligatorio | `.env` |
| `DATABASE_URL` | Inyectado por blueprint | Docker local |
| Twilio (opcional) | `TWILIO_*` secretos | `.env` |

La app **falla al arrancar** en Render si detecta secretos débiles, `DEV_AUTO_LOGIN=true`,
`APP_DEBUG=true`, o falta `OPENAI_API_KEY` / `DATABASE_URL`.

Endpoints de depuración (`POST /debug/client-log`, middleware de telemetría) quedan
**desactivados** en producción. `/debug/trace/{session_id}` sigue protegido por login web.

Headers de seguridad (HSTS, X-Frame-Options, nosniff) se aplican automáticamente en Render.

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

## GitHub Pages (tu website)

GitHub Pages **no** corre esta app Python. Tu website estática puede seguir en Pages; el agente vive solo en Render.

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

Para cierre de Fase 0, también debe verse:

- `"slack_configured": false`
- `"whatsapp_configured": false`

## Restricción de alcance (Fase 0 y Fase 1)

No activar Slack ni WhatsApp en estas fases. El despliegue de Render se usa solo
para validar la web de pruebas, autenticación, salud del servicio y chat dentro
del alcance REQ-001..REQ-011.

---

## Checklist post-deploy (Fase 0)

```bash
curl https://TU-APP.onrender.com/health
curl https://TU-APP.onrender.com/auth/status
curl -I https://TU-APP.onrender.com/
curl -I https://TU-APP.onrender.com/login
```

Resultados esperados:
- `/health` con `status=ok`, `fase_activa=0`, `web_auth_enabled=true`
- `/` redirige a login cuando no hay sesión
- `/login` disponible
- `slack_configured=false` y `whatsapp_configured=false`

---

## Plan gratis Render

- El servicio se **duerme** tras ~15 min sin uso
- El primer request puede tardar 30–60 s (cold start)
- Suficiente para desarrollo/staging

---

## GitHub Pages (tu website)

GitHub Pages **no** corre esta app Python. Tu website estática puede seguir en Pages; el agente vive solo en Render.

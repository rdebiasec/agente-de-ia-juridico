# Legal Audit Sync — Editor de configuración

Portal web para que el despacho **edite y versiona** la configuración operativa del asistente:

- Árbol **Equipos → Agentes → Prompt / Skills / Guardrails** (Input · Output · Tools)
- **Prompt sistema** (global, fuera de los grupos)
- Skills con **fuente única compartida** entre agentes

Cada guardado escribe una versión **inmutable** en Postgres (`config_versions`) y actualiza el puntero activo (`config_active`). Se puede **restaurar** cualquier versión en un clic.

## Carpetas

| Carpeta | Uso |
|---|---|
| `site/` | Fuente — `index.html`, `app.js`, `auth-gate.js` |
| `dist/` | Artefacto de despliegue — generado, no commitear |

## Uso local (mismo login que producción)

Sirva el portal **desde la app FastAPI** (recomendado):

```bash
# Con SITE_PASSWORD configurado en .env raíz
.venv/bin/python -m src.main
# Abrir http://127.0.0.1:8000/auditoria/
```

Login: correo del auditor + **misma** `SITE_PASSWORD` del chat + PIN (primera vez se define).

### Sin login en desarrollo

Con `DEV_AUTO_LOGIN=true` en el `.env` raíz, el portal abre sesión solo y no muestra el gate.
Ponga en `DEV_AUDIT_EMAIL` su correo habitual para seguir viendo el progreso guardado en local
(sin la variable usa `dev@local.test`, que empieza vacío). Está bloqueado en Render, con
`SESSION_COOKIE_SECURE=true` y por `validate_production_settings`, así que producción sigue
pidiendo correo + contraseña + PIN.

Tras entrar:

1. Elija un **equipo** y un **agente** (o **Prompt sistema**).
2. Bajo el agente, abra **Prompt**, **Skills** o **Guardrails** (Input · Output · Tools).
3. Edite el markdown y pulse **Guardar versión**.
4. Abra **Historial** para ver diff y **Restaurar**.

Preview estático en `:8080` (debe apuntar a la API):

```bash
AUDIT_API_BASE=http://127.0.0.1:8000 ./scripts/start-audit-portal.sh
# Abrir http://localhost:8080
```

```bash
AUDIT_API_BASE="" python scripts/generar_audit_portal.py   # mismo origen /auditoria
AUDIT_API_BASE="http://127.0.0.1:8000" python scripts/generar_audit_portal.py  # Pages / :8080
```

Abra con Cmd+Shift+R si no ve cambios.

## API (autenticada)

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/audit/config/catalog` | Índice editable (prompts / skills / guardrails) |
| GET | `/api/audit/config/agents` | Agentes + skills + keys Input/Output/Tools |
| GET | `/api/audit/config/{kind}/{key}` | Contenido activo |
| GET | `/api/audit/config/{kind}/{key}/versions` | Historial |
| POST | `/api/audit/config/save` | Guardar (lock optimista `expected_version`) |
| POST | `/api/audit/config/{kind}/{key}/restore` | Restaurar versión |

Kinds: `prompt`, `guardrail` (G1–G10 legacy en store), `skill`, `agent_guardrail` (keys `{agent_id}__{input|output|tools}`).

## Seed / migración

```bash
# Migración 0007 (tablas config_*)
alembic upgrade head

# Seed idempotente desde archivos del repo
.venv/bin/python scripts/seed_config_store.py
```

En Render el seed corre al arranque (lifespan) sin sobrescribir versiones ya activas.

## Alcance de guardrails

- **Por agente:** políticas editables Input / Output / Tools (`agent_guardrail`). El enforcement en runtime del SDK queda como tarea aparte.
- **Legacy G1–G10:** siguen versionados en el store (`kind=guardrail`); el portal ya no ofrece una vista plana de inventario. El código tripwire (`src/agents/sdk_guardrails.py`) permanece bajo control del desarrollador.

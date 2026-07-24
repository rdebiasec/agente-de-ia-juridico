# Legal Audit Sync — Editor de configuración

Portal web para que el despacho **edite y versiona** la configuración operativa del asistente:

- **Prompts** (sistema + 11 agentes)
- **Guardrails** (texto de política G1–G10)
- **Skills** (90 × `SKILL.md`)

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

Tras entrar:

1. Elija pestaña Prompts / Guardrails / Skills.
2. Edite el markdown y pulse **Guardar versión**.
3. Abra **Historial** para ver diff y **Restaurar**.

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
| GET | `/api/audit/config/catalog` | Inventario editable |
| GET | `/api/audit/config/{kind}/{key}` | Contenido activo |
| GET | `/api/audit/config/{kind}/{key}/versions` | Historial |
| POST | `/api/audit/config/save` | Guardar (lock optimista `expected_version`) |
| POST | `/api/audit/config/{kind}/{key}/restore` | Restaurar versión |

## Seed / migración

```bash
# Migración 0007 (tablas config_*)
alembic upgrade head

# Seed idempotente desde archivos del repo
.venv/bin/python scripts/seed_config_store.py
```

En Render el seed corre al arranque (lifespan) sin sobrescribir versiones ya activas.

## Alcance de guardrails

El portal edita el **texto de política** inyectado a los agentes. El código tripwire del SDK (`src/agents/sdk_guardrails.py`) permanece bajo control del desarrollador.

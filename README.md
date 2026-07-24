# Agente Jurídico — Firma virtual penal-víctimas

Asistente multi-agente para despacho colombiano especializado en **representación de víctimas en materia penal** (Ley 906). Un coordinador (POC) es la única voz frente al abogado; 10 especialistas operan como backoffice interno vía OpenAI Agents SDK (`agent.as_tool`).

**Repo:** `agente-de-ia-juridico`  
**Flujo:** Mac (desarrollo) → GitHub → Render (hosting)

Ver [DEPLOY.md](DEPLOY.md) para el flujo completo.

## Inicio rápido (Mac)

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env   # OPENAI_API_KEY, Slack, DATABASE_URL (opcional)
.venv/bin/python scripts/validate_fase0.py
.venv/bin/python -m src.main
# POST http://localhost:8000/chat  {"message": "¿Qué áreas del derecho cubre?"}
```

Sin `DATABASE_URL` la app usa un repositorio en memoria (ideal para tests rápidos).
Con Postgres local o Render usa el mismo esquema (Alembic + pgvector).

### Postgres local + producción (paridad)

| Entorno | Cómo | `DATABASE_URL` |
|---------|------|----------------|
| **Local — app en Mac** | `docker compose -f deploy/docker-compose.yml up -d db` + en `.env`: `postgresql+psycopg://agente:agente@localhost:5432/agente` | `localhost:5432` |
| **Local — todo en Docker** | `docker compose -f deploy/docker-compose.yml up -d` | compose usa `@db:5432` (automático) |
| **Producción (Render)** | `render.yaml` → base `agente-db` | inyectada por Render |

Atajo local (DB + migraciones, opcional `--ingest` para RAG):

```bash
./scripts/local_db.sh
./scripts/local_db.sh --ingest   # indexa agente/conocimiento/*.md
```

Verifique: `GET /health` → `"persistencia": "postgres"`.

Con Docker (abajo) se inyecta Postgres+pgvector para paridad con producción.

**PDF en local (Mac).** WeasyPrint necesita libs nativas de Homebrew:

```bash
brew install pango gdk-pixbuf libffi
# y al ejecutar/probar localmente expón la ruta de libs:
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python -m src.main
```

En Docker/Render las libs van en el `Dockerfile`, sin variables extra. El test de
PDF se omite automáticamente si las libs no están disponibles.

## Render (producción / staging)

1. Push a `main` en GitHub
2. Render redeploya desde `render.yaml`
3. Configura secretos en el dashboard de Render

## Docker (local — paridad dev==prod)

```bash
docker compose -f deploy/docker-compose.yml up --build
# Levanta Postgres+pgvector (db) y la app con DATABASE_URL apuntando a ella.
```

## Arquitectura

**Runtime (OpenAI Agents SDK).** Un solo interlocutor:

- **POC** `coordinador_expediente_penal` — responde al abogado (web / Slack)
- **10 especialistas** como tools internas (`as_tool`), no handoffs terminales:
  cronología, tipicidad, ruta Ley 906, víctimas, evidencia, audiencias,
  redacción, seguimiento, tutela, calidad jurídica
- **Guardrails nativos** del SDK en el POC (`input_guardrails` / `output_guardrails`)
  + disclaimer / HITL post-proceso
- Persona compartida: `agente/prompts/sistema.md`
- Conocimiento + playbooks: `agente/conocimiento/*.md` (penal-víctimas)
- Esquemas: `src/agents/schemas.py` (el redactor usa `output_type=BorradorDocumentoPenal`)

**Dos entradas de chat (misma orquestación POC):**

| Ruta | Uso |
|------|-----|
| `POST /chat` | Turno directo del POC (sesión del abogado) |
| `POST /chat/plan` → approve → execute | Plan visible al abogado; cada paso corre **vía POC + tools**, con sesión aislada (no contamina el historial del chat) |

**Persistencia, HITL y servicios.**

- Persistencia intercambiable (`src/storage/`): memoria o Postgres/pgvector (`DATABASE_URL`).
- Migraciones Alembic (`migrations/`): extensión `vector` + tablas de drafts, expedientes, deadlines, chunks.
- HITL: borradores `propuesto → en_revision → aprobado/editado/rechazado` (`src/hitl/`).
- RAG (`src/services/rag.py`): embeddings OpenAI; si fallan, **fallback local con warning** (calidad degradada).
- Tools de grounding: `buscar_en_conocimiento` / `buscar_en_expediente` (`src/mcp/tools.py`).

**UI web.** Panel Firma (`static/`) + portal de auditoría (`/auditoria/` y GitHub Pages).

**Portal de auditoría.** Editor vivo de prompts, guardrails (texto) y skills con versionado en Postgres. Login obligatorio vía API (`/api/audit/login`) con el mismo `SITE_PASSWORD` del despacho (correo + contraseña + PIN). Local y Pages deben apuntar a la API (Pages: `AUDIT_API_BASE` en el build). Ver [audit-portal/README.md](audit-portal/README.md).

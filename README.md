# Agente Jurídico — Firma virtual (web-only)

Asistente multi-agente para despacho colombiano, modelado como una firma: un orquestador enruta hacia roles transversales y litigantes por área (civil CGP, penal Ley 906). Canal único: **web**.

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

Sin `DATABASE_URL` la app usa un repositorio en memoria (ideal para pruebas).
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

**Agentes (Fase A).** `orquestador` → handoffs a roles transversales (intake, estratega, comunicación, redacción, conceptos, tutela, dependiente judicial, conocimiento) y litigantes por área (civil CGP, penal Ley 906).

- Persona compartida: `agente/prompts/sistema.md`
- Conocimiento + playbooks procesales: `agente/conocimiento/*.md`
- Esquemas estructurados: `src/agents/schemas.py`
- Expediente: `src/gateway/expediente.py`

**Persistencia, HITL y servicios (Fase B).**

- Persistencia con repositorio intercambiable (`src/storage/`): en memoria (tests/local) o Postgres/pgvector (`DATABASE_URL`). El **expediente** del caso también persiste (`Expediente`, tabla `expedientes`).
- Migraciones con **Alembic** (`alembic.ini`, `migrations/`): la migración inicial crea la extensión `vector` y las tablas `drafts`, `expedientes`, `deadlines`, `document_chunks`. Con `DATABASE_URL`, la app ejecuta `alembic upgrade head` al arrancar (fallback a `create_all` si algo falla).
- Revisión humana (HITL): todo borrador accionable se guarda como `Draft` y pasa por estados `propuesto → en_revision → aprobado/editado/rechazado` (`src/hitl/`).
  - Bandeja del abogado y acciones: `GET /drafts/pendientes`, `POST /drafts/{id}/approve|reject|edit`, `GET /drafts/{id}/docx`.
  - Aprobación desde Slack: botones Block Kit + webhook firmado `POST /slack/interactivity`.
- Términos procesales: días hábiles con festivos de Colombia (`src/services/plazos.py`; tutela 10 días). API: `GET/POST /deadlines`, `PATCH /deadlines/{id}`. Al aprobar una tutela se crea automáticamente su término de fallo.
- Recordatorios programados: `src/services/scheduler.py` (APScheduler) arranca en el `lifespan`, marca términos vencidos y envía alertas a Slack (job diario) más un recordatorio mensual de seguimiento. La clasificación de vencimientos es una función pura testeable (`clasificar_vencimientos`).
- Documentos: generación de `.docx`/`.pdf` y extracción de texto de PDF/Word (`src/services/documentos.py`; `POST /documents/extract`, `GET /drafts/{id}/docx`, `GET /drafts/{id}/pdf`).
- **RAG** (`src/services/rag.py`): chunking + embeddings (OpenAI `text-embedding-3-small`, con fallback local determinista) sobre `pgvector`, en una sola tabla `document_chunks` con dos alcances (`kb` de la firma y `expediente` del caso).
  - Indexar la KB: `POST /rag/ingest-kb` o `scripts/ingest_kb.py`.
  - Ingestar un adjunto a un caso: `POST /documents/extract` con `expediente_id` e `ingestar=true`.
  - Buscar: `POST /rag/search`. Los agentes citan vía las tools `buscar_en_conocimiento` / `buscar_en_expediente`.

**UI web (panel "Firma").** Botón *Bandeja del abogado* en la cabecera abre el panel (`static/firma.js`, `static/index.html`) con: bandeja de borradores pendientes (aprobar/editar/rechazar, descargar `.docx`/`.pdf`), subida de documentos al expediente con ingesta RAG, búsqueda semántica y gestión de términos. Cuando el chat genera un borrador, muestra un aviso "enviado a la bandeja" y refresca el panel.

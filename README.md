# Agente Jurídico — Firma virtual (web-only)

Asistente multi-agente para despacho colombiano, modelado como una firma: un orquestador enruta hacia roles transversales y litigantes por área (civil CGP, penal Ley 906). Canal único: **web**.

**Repo:** `agente-de-ia-juridico`  
**Flujo:** Mac (desarrollo) → GitHub → Render (hosting)

Ver [DEPLOY.md](DEPLOY.md) para el flujo completo.

## Inicio rápido (Mac)

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env   # OPENAI_API_KEY, Slack, Twilio
.venv/bin/python scripts/validate_fase0.py
.venv/bin/python -m src.main
# POST http://localhost:8000/chat  {"message": "¿Qué áreas del derecho cubre?"}
```

## Render (producción / staging)

1. Push a `main` en GitHub
2. Render redeploya desde `render.yaml`
3. Configura secretos en el dashboard de Render

## Docker (local)

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
docker compose -f deploy/docker-compose.yml up
```

## Arquitectura (Fase A — local, sin estado)

- `orquestador` → handoffs a roles transversales (intake, estratega, comunicación, redacción, conceptos, tutela, dependiente judicial, conocimiento) y litigantes por área (civil, penal).
- Persona compartida: `agente/prompts/sistema.md`
- Base de conocimiento + playbooks procesales: `agente/conocimiento/*.md`
- Esquemas estructurados: `src/agents/schemas.py`
- Expediente en memoria (seam para persistencia futura): `src/gateway/expediente.py`

La persistencia (PostgreSQL/pgvector vía Docker), HITL en Slack, RAG y plazos se abordan en la Fase B. Ver `docs/plan-rediseno-firma.md`.

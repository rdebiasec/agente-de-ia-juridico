# Agente Jurídico — Fase 0

Asistente multi-agente para despacho colombiano. Canales: **Slack** y **WhatsApp**.

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

## Arquitectura Fase 0

- `orquestador_fase0` → handoff a perfil o conocimiento
- Base conocimiento: `agente/conocimiento/*.md`
- WhatsApp (Twilio): `POST /whatsapp/webhook`
- Slack: Socket Mode si hay `SLACK_BOT_TOKEN`

## Fases

| Fase | Estado |
|------|--------|
| 0 | Activa |
| 1–3 | Stub en `agente/fases/` |

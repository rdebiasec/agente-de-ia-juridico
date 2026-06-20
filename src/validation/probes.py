"""Generación dinámica de preguntas de validación Fase 0 vía LLM."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from src.config import get_settings
from src.validation.rubric import (
    GENERATABLE_BLOCK_IDS,
    VALIDATION_BLOCKS,
    default_probes_by_block,
)

logger = logging.getLogger(__name__)

_last_generate: dict[str, float] = {}
GENERATE_COOLDOWN_SEC = 10


def _check_rate_limit(user_id: str) -> None:
    now = time.monotonic()
    last = _last_generate.get(user_id, 0.0)
    if now - last < GENERATE_COOLDOWN_SEC:
        raise ValueError("Espere unos segundos antes de generar nuevas preguntas.")
    _last_generate[user_id] = now


def _build_prompt(probes_per_block: int) -> str:
    blocks_text = []
    for block in VALIDATION_BLOCKS:
        blocks_text.append(
            f'- id: "{block["id"]}"\n'
            f"  objetivo: {block['generation_goal']}\n"
            f"  intención: {block['question_intent']}\n"
            f"  prohibido: {block['must_not']}"
        )
    blocks_joined = "\n".join(blocks_text)
    return f"""Eres un generador de preguntas de prueba para validar un asistente jurídico colombiano (Fase 0).

Genera exactamente {probes_per_block} preguntas DISTINTAS por cada bloque listado.
Cada pregunta debe probar la MISMA función del bloque pero con redacción diferente:
formal, informal, como cliente, como abogada junior, indirecta, directa, etc.
Español colombiano. No inventes datos del despacho.

Bloques:
{blocks_joined}

Responde SOLO JSON válido con esta forma:
{{
  "blocks": {{
    "profile": [{{"label": "descripción corta", "message": "texto exacto a enviar al chat"}}],
    "areas": [...],
    "phase-block": [...],
    "disclaimer": [...],
    "integrity": [...]
  }}
}}

Reglas:
- "message" es lo que se envía tal cual al chat (una sola pregunta o solicitud).
- "label" resume la variante en pocas palabras para la UI.
- No repitas la misma redacción dentro del bloque.
"""


async def generate_probes(
    user_id: str = "web",
    blocks: list[str] | None = None,
    probes_per_block: int = 2,
) -> dict[str, Any]:
    """Genera preguntas variadas por bloque. Fallback a defaults sin API key."""
    _check_rate_limit(user_id)

    block_ids = blocks or GENERATABLE_BLOCK_IDS
    invalid = [b for b in block_ids if b not in GENERATABLE_BLOCK_IDS]
    if invalid:
        raise ValueError(f"Bloques no reconocidos: {', '.join(invalid)}")

    probes_per_block = max(1, min(probes_per_block, 4))
    settings = get_settings()
    session_id = f"val-{uuid.uuid4().hex[:12]}"
    fallback = default_probes_by_block()

    if not settings.openai_api_key:
        return {
            "session_id": session_id,
            "source": "fallback",
            "blocks": {bid: fallback.get(bid, [])[:probes_per_block] for bid in block_ids},
        }

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Respondes únicamente JSON válido."},
                {"role": "user", "content": _build_prompt(probes_per_block)},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        generated: dict[str, list[dict[str, str]]] = data.get("blocks", {})

        result_blocks: dict[str, list[dict[str, str]]] = {}
        for bid in block_ids:
            probes = generated.get(bid, [])
            cleaned = []
            for p in probes[:probes_per_block]:
                label = str(p.get("label", "")).strip()
                message = str(p.get("message", "")).strip()
                if label and message:
                    cleaned.append({"label": label, "message": message})
            if not cleaned:
                cleaned = fallback.get(bid, [])[:probes_per_block]
            result_blocks[bid] = cleaned[:probes_per_block]

        return {"session_id": session_id, "source": "llm", "blocks": result_blocks}

    except Exception as exc:
        logger.warning("Fallo generación LLM de probes: %s", exc)
        return {
            "session_id": session_id,
            "source": "fallback",
            "blocks": {bid: fallback.get(bid, [])[:probes_per_block] for bid in block_ids},
        }

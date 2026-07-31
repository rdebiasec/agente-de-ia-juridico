"""Precios orientativos OpenAI ($/1M tokens) para forecast de traza (B04/B06).

Actualizar cuando cambie la tarjeta oficial; no son facturación en tiempo real.
"""

from __future__ import annotations

# USD por 1M tokens (input, output). Fuente: pricing OpenAI ~2026-07.
_MODEL_PRICES_USD_PER_1M: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-5-mini": (0.25, 2.00),
}


def price_for_model(model: str | None) -> tuple[float, float] | None:
    """Devuelve (input_$/1M, output_$/1M) o None si el modelo no está en tabla."""
    if not model:
        return None
    key = str(model).strip().lower()
    if key in _MODEL_PRICES_USD_PER_1M:
        return _MODEL_PRICES_USD_PER_1M[key]
    # Snapshots tipo gpt-4.1-mini-2025-04-14
    for known, prices in _MODEL_PRICES_USD_PER_1M.items():
        if key.startswith(known):
            return prices
    return None


def estimate_call_cost_usd(
    *,
    model: str | None,
    input_tokens: int,
    output_tokens: int,
) -> float | None:
    prices = price_for_model(model)
    if prices is None:
        return None
    in_rate, out_rate = prices
    return (max(0, input_tokens) * in_rate + max(0, output_tokens) * out_rate) / 1_000_000.0


def enrich_completion_with_cost(calls: list[dict]) -> dict:
    """Añade estimated_cost_usd por call y resume costo del turno."""
    total = 0.0
    known = 0
    for call in calls:
        usage = call.get("usage") or {}
        cost = estimate_call_cost_usd(
            model=call.get("model"),
            input_tokens=int(usage.get("input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
        )
        if cost is None:
            call["estimated_cost_usd"] = None
            continue
        call["estimated_cost_usd"] = round(cost, 6)
        total += cost
        known += 1
    return {
        "estimated_cost_usd": round(total, 6) if known else None,
        "priced_calls": known,
        "unpriced_calls": max(0, len(calls) - known),
    }

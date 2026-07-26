"""Cache de agentes por fingerprint de config (G2)."""

from __future__ import annotations

from typing import Any, Callable

_ORCH_CACHE: dict[tuple[Any, ...], Any] = {}
_AGENT_CACHE: dict[tuple[str, str], Any] = {}


def config_fingerprint() -> str:
    """Huella de prompts activos + modelos relevantes para invalidar cache."""
    from src.config import get_settings

    parts: list[str] = []
    try:
        from src.config_store import KIND_PROMPT, get_active_content

        for key in ("sistema", "coordinador_expediente_penal"):
            try:
                data = get_active_content(KIND_PROMPT, key)
                parts.append(
                    f"{key}:{data.get('version')}:{str(data.get('checksum') or '')[:12]}"
                )
            except Exception:
                parts.append(f"{key}:fallback")
    except Exception:
        parts.append("config_store:unavailable")

    settings = get_settings()
    parts.append(
        "m:"
        f"{settings.openai_model}:"
        f"{settings.openai_model_high_risk}:"
        f"{settings.agent_nested_max_turns}:"
        f"{settings.agent_max_turns}"
    )
    return "|".join(parts)


def clear_agent_cache() -> None:
    _ORCH_CACHE.clear()
    _AGENT_CACHE.clear()


def get_cached_orchestrator(
    builder: Callable[..., Any],
    *,
    require_tool_approval: bool,
    include_high_risk_tools: bool,
    focus_agent_id: str | None,
    include_kb_search_tool: bool,
    include_full_read_tools: bool,
    slim_instructions: bool,
    include_list_areas_tool: bool = False,
) -> Any:
    key = (
        config_fingerprint(),
        require_tool_approval,
        include_high_risk_tools,
        focus_agent_id or "",
        include_kb_search_tool,
        include_full_read_tools,
        slim_instructions,
        include_list_areas_tool,
    )
    cached = _ORCH_CACHE.get(key)
    if cached is not None:
        return cached
    agent = builder(
        require_tool_approval=require_tool_approval,
        include_high_risk_tools=include_high_risk_tools,
        focus_agent_id=focus_agent_id,
        include_kb_search_tool=include_kb_search_tool,
        include_full_read_tools=include_full_read_tools,
        include_list_areas_tool=include_list_areas_tool,
        slim_instructions=slim_instructions,
        use_cache=False,
    )
    _ORCH_CACHE[key] = agent
    return agent


def get_cached_agent(agent_id: str, builder: Callable[[], Any]) -> Any:
    key = (config_fingerprint(), agent_id)
    cached = _AGENT_CACHE.get(key)
    if cached is not None:
        return cached
    agent = builder()
    _AGENT_CACHE[key] = agent
    return agent


def cache_stats() -> dict[str, int]:
    return {
        "orchestrator_entries": len(_ORCH_CACHE),
        "agent_entries": len(_AGENT_CACHE),
    }

"""Ensamblaje de instrucciones slim (G2/G4) — políticas largas viven en guardrails SDK."""

from __future__ import annotations


_SLIM_SYSTEM = """Eres parte de una firma virtual penal-víctimas (Colombia, Ley 906).
Apoyas al abogado titular: propones; él revisa, decide y firma.
Reglas innegociables: no inventes normas, sentencias, radicados ni hechos;
marca `[PENDIENTE DE VERIFICAR]` lo no soportado; salidas accionables requieren revisión humana.
"""

# G-ids alineados a config/guardrails/g1..g10.md (fuente canónica de políticas).
# No declarar enforcement que no exista: el runtime aplica un subconjunto vía
# sdk_guardrails / completeness / plan HITL; el resto es obligación de instrucción.
_SLIM_POLICY_HINT = (
    "Políticas obligatorias del despacho (ids = config/guardrails/g1..g10.md; "
    "subset enforced en código/SDK): "
    "g1 no inventar; g2 pedir datos faltantes; g3 separar hecho/inferencia; "
    "g4 revisión humana obligatoria; g5 no revictimizar; g6 confidencialidad; "
    "g7 fuera de alcance; g8 aviso de borrador; g9 oportunidad/términos Ley 906; "
    "g10 integridad probatoria. "
    "Código/SDK: alcance duro, PII, tripwires de salida vacía, "
    "routing tutela→evaluador y gates de plan/completitud — no reexpongas textos largos."
)


def slim_system_prompt() -> str:
    return _SLIM_SYSTEM.strip()


def slim_policy_block() -> str:
    return _SLIM_POLICY_HINT


def load_role_prompt(agent_id: str) -> str:
    from src.config import get_settings
    from src.config_store import load_prompt_text

    try:
        return load_prompt_text(agent_id).strip()
    except Exception:
        path = get_settings().agente_dir / "prompts" / "agents" / f"{agent_id}.md"
        return path.read_text(encoding="utf-8").strip()


def load_full_system_prompt() -> str:
    from src.config import get_settings
    from src.config_store import load_prompt_text

    try:
        return load_prompt_text("sistema")
    except Exception:
        path = get_settings().agente_dir / "prompts" / "sistema.md"
        return path.read_text(encoding="utf-8")


def full_policy_block(agent_id: str | None = None) -> str:
    """Políticas G1–G10 + agent_guardrail Input/Output/Tools (modo legacy/verbose)."""
    parts: list[str] = []
    try:
        from src.config_store import load_guardrail_policies

        policies = load_guardrail_policies()
    except Exception:
        policies = []
    if policies:
        lines = ["Políticas obligatorias del despacho (guardrails de política):"]
        for g in policies:
            lines.append(f"- [{g['id']}] {g['name']}: {g['desc']}")
        parts.append("\n".join(lines))

    if agent_id:
        try:
            from src.config_store import KIND_AGENT_GUARDRAIL, get_active_content
            from src.config_store.paths import agent_guardrail_key
            from src.config_store.service import strip_header
        except Exception:
            return "\n\n".join(parts)

        labels = {"input": "INPUT", "output": "OUTPUT", "tools": "TOOLS"}
        for clase, label in labels.items():
            try:
                data = get_active_content(
                    KIND_AGENT_GUARDRAIL, agent_guardrail_key(agent_id, clase)
                )
                body = strip_header((data.get("content") or "")).strip()
                if body:
                    parts.append(f"### Guardrails de agente ({label})\n{body}")
            except Exception:
                continue
    return "\n\n".join(parts)


def assemble_instructions(
    agent_id: str,
    *,
    slim: bool = True,
    backoffice: bool = False,
    backoffice_voice: str = "",
    capability_anchor: str = "",
) -> str:
    """Compone instructions. slim=True omite dumps largos (G1–G10 bodies + agent guardrails)."""
    if slim:
        parts = [slim_system_prompt(), load_role_prompt(agent_id)]
    else:
        parts = [load_full_system_prompt(), load_role_prompt(agent_id)]
    if backoffice and backoffice_voice.strip():
        parts.append(backoffice_voice.strip())
    if capability_anchor.strip():
        brief = capability_anchor.strip()
        if slim and len(brief) > 500:
            brief = brief[:497] + "..."
        parts.append(brief)
    if slim:
        parts.append(slim_policy_block())
    else:
        policy = full_policy_block(agent_id)
        if policy:
            parts.append(policy)
    return "\n\n".join(parts) + "\n"


def instruction_stats(text: str) -> dict[str, int]:
    return {"chars": len(text or ""), "approx_tokens": max(1, len(text or "") // 4)}

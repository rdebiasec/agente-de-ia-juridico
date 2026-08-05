"""Ensamblaje de instrucciones slim (G2/G4) — políticas largas viven en guardrails SDK."""

from __future__ import annotations


_SLIM_SYSTEM = """Eres parte de una firma virtual penal-víctimas (Colombia, Ley 906).
Apoyas al abogado titular: propones; él revisa, decide y firma.
Reglas innegociables: no inventes normas, sentencias, radicados ni hechos;
marca `[PENDIENTE DE VERIFICAR]` lo no soportado; salidas accionables requieren revisión humana.
"""

# Fuente de verdad: desk_policies + I/O/T por agente + SDK/HITL.
# Ids legacy g1…g10 son solo alias de portal; no son frenos por sí solos.
_SLIM_POLICY_HINT = (
    "Políticas obligatorias del despacho "
    "(canónicas: config/guardrails/_shared/desk_policies.md; "
    "enforcement: agents/{id}/{input|output|tools}.md + SDK/HITL): "
    "no_inventar; pedir_faltantes; hecho_vs_inferencia; hitl; "
    "no_revictimizar; confidencialidad; fuera_de_alcance; aviso_borrador; "
    "terminos_906; integridad_probatoria. "
    "Código/SDK: alcance duro, PII, tripwires de salida vacía, "
    "gates de plan/completitud — no reexpongas textos largos."
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
    """desk_policies (+ alias g*) + agent_guardrail Input/Output/Tools (modo verbose)."""
    parts: list[str] = []
    try:
        from src.config_store import load_guardrail_policies

        policies = load_guardrail_policies()
    except Exception:
        policies = []
    if policies:
        lines = [
            "Políticas obligatorias del despacho "
            "(I/O/T + SDK; ids g* = alias deprecados de portal):"
        ]
        for g in policies:
            pid = g.get("policy_id") or g["id"]
            status = g.get("status") or "active"
            tag = f"{pid}" if status != "deprecated" else f"{pid} (alias {g['id']})"
            lines.append(f"- [{tag}] {g['name']}: {g['desc']}")
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
    """Compone instructions. slim=True omite dumps largos (desk_policies + agent I/O/T)."""
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

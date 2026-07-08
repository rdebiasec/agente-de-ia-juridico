#!/usr/bin/env python3
"""Remediación g2, g9, g10 globales y cobertura g4/g5/Rol en SKILL.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import SKILLS_DIR, load_skills_catalog  # noqa: E402

MIRROR = ROOT / "agente" / "skills"

LINES = {
    "g4_internal": "- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.",
    "g4_report": "- **g4:** HITL obligatorio antes de compartir reporte con cliente o terceros; uso interno despacho con revisión.",
    "g4_revictim": "- **g4:** HITL obligatorio antes de incorporar hallazgos a escritos o comunicación externa.",
    "g5": "- **g5:** Lenguaje respetuoso con la víctima; sin juicios de credibilidad ni exposición innecesaria.",
    "g9": "- **g9:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.",
    "g10": "- **g10:** No sugerir descarte de evidencia sin revisar custodia, preservación y cadena probatoria.",
}

CATEGORIES_G5 = {
    "Skills de representacion de victimas",
    "Skills de hechos y cronologia",
}

CATEGORIES_G9_G10 = {
    "Skills de ruta procesal Ley 906",
    "Skills de seguimiento procesal",
    "Skills de evidencia y soporte probatorio",
}

EXTRA_G9 = {
    "controlar_terminos_procesales_preliminares",
    "generar_alertas_terminos_vencimientos",
    "evaluar_oportunidad_procesal",
    "detectar_inactividad_procesal",
}

G4_REPORT_SKILLS = {"crear_reporte_estado_caso", "preparar_resumen_operativo_cliente"}
G4_REVICTIM = {"detectar_riesgo_revictimizacion", "analizar_derechos_victima", "analizar_enfoque_diferencial", "evaluar_dano_y_afectacion"}

ROL_BLOCKS: dict[str, tuple[str, str]] = {
    "clasificar_tipo_prueba": (
        "gestor_evidencia",
        "Tipificación que alimenta matriz hecho-prueba y evaluación de fuerza probatoria.",
    ),
    "controlar_confidencialidad_datos_sensibles": (
        "calidad",
        "Control de minimización y datos sensibles antes de salidas externas.",
    ),
    "crear_reporte_estado_caso": (
        "gestor_seguimiento",
        "Panorama operativo interno para el despacho; no sustituye memorial ni comunicación con cliente.",
    ),
    "estructurar_hechos_fundamentos_solicitudes": (
        "redactor",
        "Esquema previo a redacción de escritos; insumo del redactor, no pieza final.",
    ),
    "identificar_derecho_fundamental_afectado": (
        "evaluador_tutela",
        "Primer filtro constitucional antes de subsidiariedad y procedencia.",
    ),
    "identificar_intereses_victima": (
        "representacion_victima",
        "Traduce hechos y contexto en objetivos de representación centrada en la víctima.",
    ),
    "inventariar_evidencia": (
        "gestor_evidencia",
        "Base del inventario probatorio; antecede clasificación, matrices y brechas.",
    ),
    "monitorear_radicado": (
        "gestor_seguimiento",
        "Consulta puntual de estado; alimenta alertas y reportes de seguimiento.",
    ),
    "preparar_contraargumentos": (
        "preparador_audiencias",
        "Réplicas anticipadas para audiencia o memorial; insumo estratégico, no conclusión.",
    ),
    "preparar_preguntas_audiencia": (
        "preparador_audiencias",
        "Guion probatorio oral alineado con hechos y teoría del caso.",
    ),
    "redactar_ampliacion_denuncia": (
        "redactor",
        "Borrador de ampliación; HITL y radicación son del despacho.",
    ),
    "registrar_actuacion_procesal": (
        "gestor_seguimiento",
        "Bitácora operativa del expediente para cronología y reportes.",
    ),
    "seguimiento_documentos_radicados": (
        "gestor_seguimiento",
        "Seguimiento de peticiones y respuestas; alerta vencimientos y faltantes.",
    ),
}


def _has_tag(text: str, tag: str) -> bool:
    return bool(re.search(rf"\*\*{tag}:\*\*|\b{tag}\b", text, re.I))


def _insert_guardrail_line(body: str, line: str, tag: str) -> str:
    if _has_tag(body, tag):
        return body
    m = re.search(r"(## Guardrails[^\n]*\n)(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return body
    section = m.group(2)
    if re.search(r"^\s*-\s*\*\*g8", section, re.M):
        section = re.sub(
            r"(^\s*-\s*\*\*g8[^\n]*)",
            line + "\n\\1",
            section,
            count=1,
            flags=re.M,
        )
    else:
        section = section.rstrip() + "\n" + line + "\n"
    return body[: m.start(2)] + section + body[m.end(2) :]


def _add_rol(body: str, sid: str) -> str:
    if "## Rol en" in body or sid not in ROL_BLOCKS:
        return body
    agent_key, desc = ROL_BLOCKS[sid]
    block = f"\n## Rol en {agent_key}\n{desc}\n"
    m = re.search(r"(## Purpose\n.*?\n)(## )", body, re.S)
    if m:
        return body[: m.end(1)] + block + body[m.start(2) :]
    return body


def patch_skill(path: Path, sid: str, category: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = re.sub(r"## Guardrails \(g1–g8\)", "## Guardrails (g1–g10)", text)
    text = re.sub(r"## Guardrails \(g1-g8\)", "## Guardrails (g1-g10)", text)

    if category in CATEGORIES_G5:
        text = _insert_guardrail_line(text, LINES["g5"], "g5")

    if category in CATEGORIES_G9_G10 or sid in EXTRA_G9:
        text = _insert_guardrail_line(text, LINES["g9"], "g9")
        text = _insert_guardrail_line(text, LINES["g10"], "g10")

    if not _has_tag(text, "g4"):
        if sid in G4_REPORT_SKILLS:
            text = _insert_guardrail_line(text, LINES["g4_report"], "g4")
        elif sid in G4_REVICTIM:
            text = _insert_guardrail_line(text, LINES["g4_revictim"], "g4")
        else:
            text = _insert_guardrail_line(text, LINES["g4_internal"], "g4")

    text = _add_rol(text, sid)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def sync_mirror(sid: str) -> None:
    src = SKILLS_DIR / sid / "SKILL.md"
    dst = MIRROR / sid / "SKILL.md"
    if src.is_file() and dst.parent.is_dir():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    catalog = load_skills_catalog()
    changed = 0
    for sid in sorted(catalog):
        category = catalog[sid].get("category") or ""
        path = SKILLS_DIR / sid / "SKILL.md"
        if not path.is_file():
            continue
        if patch_skill(path, sid, category):
            changed += 1
            sync_mirror(sid)
    print(f"SKILL.md actualizados: {changed}")


if __name__ == "__main__":
    main()

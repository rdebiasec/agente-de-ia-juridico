"""Catalogo compartido: agentes, guardrails y parsers de skills."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _resolve_skills_dir() -> Path:
    """Fuente canónica: `agente/skills` (runtime/CI). `.cursor/skills` es espejo IDE."""
    canonical = ROOT / "agente" / "skills"
    if canonical.is_dir() and any(canonical.glob("*/SKILL.md")):
        return canonical
    mirror = ROOT / ".cursor" / "skills"
    if mirror.is_dir() and any(mirror.glob("*/SKILL.md")):
        return mirror
    return canonical


SKILLS_DIR = _resolve_skills_dir()
LISTA = ROOT / "docs" / "canon" / "lista-aprobacion-agentes-skills-pasos.md"

_FALLBACK_GUARDRAILS = [
    {
        "id": "g1",
        "name": "No inventar",
        "desc": "Si no hay fuente verificada, se marca como pendiente de verificar.",
    },
    {
        "id": "g2",
        "name": "Pedir datos faltantes",
        "desc": "Si faltan hechos, etapa, radicado o plazos Ley 906, el sistema pregunta antes de concluir.",
    },
    {
        "id": "g3",
        "name": "Separar hecho de inferencia",
        "desc": "Distingue lo confirmado, lo narrado y lo inferido.",
    },
    {
        "id": "g4",
        "name": "Revision humana obligatoria",
        "desc": "Escritos, estrategia, memoriales y reportes a cliente requieren aprobacion.",
    },
    {
        "id": "g5",
        "name": "No revictimizar",
        "desc": "El lenguaje no culpa ni expone indebidamente a la victima.",
    },
    {
        "id": "g6",
        "name": "Confidencialidad",
        "desc": "Detecta y controla datos sensibles innecesarios.",
    },
    {
        "id": "g7",
        "name": "Fuera de alcance",
        "desc": "Consultas no penales se declaran fuera de alcance penal-victimas.",
    },
    {
        "id": "g8",
        "name": "Aviso de borrador",
        "desc": "Toda respuesta termina con aviso de revision profesional.",
    },
    {
        "id": "g9",
        "name": "Oportunidad y terminos Ley 906",
        "desc": "No recomendar actuacion sin verificar plazos, notificaciones y etapa; extemporaneidad marcada pendiente hasta confirmacion del abogado.",
    },
    {
        "id": "g10",
        "name": "Integridad probatoria",
        "desc": "No alterar ni suprimir evidencia; cadena de custodia y preservacion digital antes de descartar prueba en estrategia.",
    },
]


def _load_guardrails() -> list[dict]:
    """Carga políticas desde config/guardrails/*.md (o DB vía config_store si disponible)."""
    try:
        from src.config_store import load_guardrail_policies

        loaded = load_guardrail_policies()
        if loaded:
            return loaded
    except Exception:
        pass
    guard_dir = ROOT / "config" / "guardrails"
    if not guard_dir.is_dir():
        return list(_FALLBACK_GUARDRAILS)
    items: list[dict] = []
    for path in sorted(guard_dir.glob("g*.md")):
        text = path.read_text(encoding="utf-8")
        name = path.stem
        gid = path.stem
        body_lines: list[str] = []
        for ln in text.splitlines():
            if ln.startswith("# "):
                name = ln[2:].strip() or name
            elif ln.startswith("id:"):
                gid = ln.split(":", 1)[1].strip() or gid
            elif ln.startswith("name:"):
                name = ln.split(":", 1)[1].strip() or name
            elif ln.strip():
                body_lines.append(ln.strip())
        items.append({"id": gid, "name": name, "desc": " ".join(body_lines).strip()})
    return items or list(_FALLBACK_GUARDRAILS)


GUARDRAILS = _load_guardrails()

AGENT_TITULOS: dict[str, str] = {
    "coordinador_caso": "COORDINACIÓN OPERATIVA DEL CASO — VÍCTIMAS",
    "analista_cronologia_hechos": "RECONSTRUCCIÓN CRONOLÓGICA DEL HECHO PENAL",
    "analista_responsabilidad_tipicidad": "ANÁLISIS DE TIPICIDAD Y RESPONSABILIDAD PENAL",
    "analista_ruta_procesal": "ESTRATEGIA PROCESAL BAJO LA LEY 906 DE 2004",
    "analista_representacion_victimas": "REPRESENTACIÓN JURÍDICA CENTRADA EN LA VÍCTIMA",
    "analista_evidencia": "GESTIÓN PROBATORIA Y SOPORTE DE EVIDENCIA",
    "analista_audiencias": "PREPARACIÓN ESTRATÉGICA DE AUDIENCIAS PENALES",
    "redactor_documentos_juridicos": "REDACCIÓN DE ESCRITOS Y MEMORIALES PENALES",
    "analista_seguimiento_procesal": "SEGUIMIENTO Y CONTROL DEL EXPEDIENTE PENAL",
    "analista_calidad_juridica": "REVISIÓN DE CALIDAD Y CONTROL DE RIESGOS JURÍDICOS",
}

DESTINATARIO_BY_AGENT: dict[str, str] = {
    "coordinador_caso": "Siguiente agente o guía operativa del caso",
    "redactor_documentos_juridicos": "Despacho (borrador para firma y radicación)",
    "analista_calidad_juridica": "Despacho (dictamen de conformidad)",
    "analista_seguimiento_procesal": "Despacho (alertas y estado del expediente)",
    "analista_audiencias": "Despacho (insumos para audiencia)",
}

AGENTS = [
    {
        "id": "coordinador_caso",
        "nombre_corto": "Coordinador del Caso",
        "titulo_profesional": "COORDINACIÓN OPERATIVA DEL CASO — VÍCTIMAS",
        "proposito": "Coordina el caso: recibe la consulta, verifica completitud y prioridad, asigna al especialista correcto y responde con una sola voz de despacho.",
        "problema": "Evita respuestas mal enfocadas y actuaciones sobre expedientes incompletos; ordena el trabajo por prioridad legal y urgencia.",
        "necesidad": "En penal-victimas la estrategia cambia por etapa Ley 906; esta coordinación reduce errores de enfoque y pérdida de términos.",
        "no_reemplaza": "El analisis de fondo por especialidad ni la aprobacion y firma final del abogado titular.",
        "prompt_simple": [
            "Solo trabaja en casos de penal-victimas en Colombia.",
            "Antes de todo, verifica que el caso tenga los datos y documentos minimos.",
            "Decide a que especialista enviar cada consulta segun necesidad del caso.",
            "Si faltan datos importantes, primero los pide antes de dar una conclusion.",
            "No inventa normas, sentencias, radicados ni hechos.",
        ],
    },
    {
        "id": "analista_cronologia_hechos",
        "nombre_corto": "Cronología y Hechos",
        "titulo_profesional": "RECONSTRUCCIÓN CRONOLÓGICA DEL HECHO PENAL",
        "proposito": "Convierte relatos y documentos en una historia factual ordenada y verificable.",
        "problema": "Evita contradicciones y vacios de hecho que debilitan memoriales o solicitudes.",
        "necesidad": "En litigio penal, la consistencia factual impacta tipicidad, audiencia y credibilidad.",
        "no_reemplaza": "La calificacion penal definitiva.",
        "prompt_simple": [
            "Ordena hechos en linea de tiempo con fechas y actores.",
            "Separa hechos confirmados, narrados e inferidos.",
            "Detecta contradicciones y vacios factuales.",
            "No inventa hechos ni fuentes.",
        ],
    },
    {
        "id": "analista_responsabilidad_tipicidad",
        "nombre_corto": "Tipicidad y Responsabilidad",
        "titulo_profesional": "ANÁLISIS DE TIPICIDAD Y RESPONSABILIDAD PENAL",
        "proposito": "Traduce hechos y pruebas en hipotesis juridicas de tipicidad y responsabilidad preliminar.",
        "problema": "Evita pedir actuaciones sin base tipica suficiente o con riesgo de atipicidad.",
        "necesidad": "Determina pertinencia de intervenciones en Ley 906 y fortalece teoria de caso de victima.",
        "no_reemplaza": "El juicio del despacho sobre imputacion, acusacion o estrategia final.",
        "prompt_simple": [
            "Analiza tipicidad, autoria, participacion y dolo/culpa de forma preliminar.",
            "Identifica agravantes, atenuantes y riesgos de atipicidad.",
            "No afirma conclusiones definitivas.",
            "No inventa normas ni jurisprudencia.",
        ],
    },
    {
        "id": "analista_ruta_procesal",
        "nombre_corto": "Ruta Procesal Ley 906",
        "titulo_profesional": "ESTRATEGIA PROCESAL BAJO LA LEY 906 DE 2004",
        "proposito": "Ubica la etapa exacta y la mejor ruta procesal para representar a la victima.",
        "problema": "Evita extemporaneidad, improcedencia y solicitudes mal dirigidas.",
        "necesidad": "Ley 906 exige precision de oportunidad y forma en cada actuacion.",
        "no_reemplaza": "El seguimiento operativo diario del radicado.",
        "prompt_simple": [
            "Identifica etapa procesal y oportunidades de intervencion.",
            "Evalua terminos, riesgos procesales y actuaciones posibles.",
            "Propone ruta recomendada para la victima.",
            "No hace seguimiento operativo diario.",
        ],
    },
    {
        "id": "analista_representacion_victimas",
        "nombre_corto": "Representación de Víctimas",
        "titulo_profesional": "REPRESENTACIÓN JURÍDICA CENTRADA EN LA VÍCTIMA",
        "proposito": "Garantiza que la estrategia este centrada en derechos, intereses y no revictimizacion.",
        "problema": "Evita estrategias tecnicamente correctas pero desconectadas del objetivo real de la victima.",
        "necesidad": "La representacion de victimas exige enfoque diferencial y proteccion de derechos fundamentales.",
        "no_reemplaza": "La decision politica o reputacional del despacho sobre el caso.",
        "prompt_simple": [
            "Construye teoria del caso desde derechos e intereses de la victima.",
            "Evalua dano, afectacion y riesgo de revictimizacion.",
            "Aplica enfoque diferencial cuando corresponda.",
            "No promete resultados judiciales.",
        ],
    },
    {
        "id": "analista_evidencia",
        "nombre_corto": "Evidencia y Pruebas",
        "titulo_profesional": "GESTIÓN PROBATORIA Y SOPORTE DE EVIDENCIA",
        "proposito": "Transforma evidencia dispersa en inventario util y plan probatorio accionable.",
        "problema": "Reduce perdida de evidencia, falta de cadena de custodia y brechas probatorias.",
        "necesidad": "Sin soporte probatorio claro, la estrategia de victima se debilita en audiencia y escritos.",
        "no_reemplaza": "La pericia tecnica forense ni la cadena de custodia certificada.",
        "prompt_simple": [
            "Inventaria evidencia y construye matriz hecho-prueba.",
            "Detecta brechas y propone plan de recaudo.",
            "Marca escalamiento cuando la cadena de custodia es estricta.",
            "No altera ni manipula evidencia.",
        ],
    },
    {
        "id": "analista_audiencias",
        "nombre_corto": "Audiencias Penales",
        "titulo_profesional": "PREPARACIÓN ESTRATÉGICA DE AUDIENCIAS PENALES",
        "proposito": "Prepara audiencias con objetivo, guion, preguntas y solicitudes.",
        "problema": "Evita improvisacion y omisiones tacticas.",
        "necesidad": "Las audiencias en Ley 906 son determinantes y exigen preparacion tecnica previa.",
        "no_reemplaza": "La intervencion oral de quien representa en estrados.",
        "prompt_simple": [
            "Define objetivo juridico y tactico de la audiencia.",
            "Prepara guion, solicitudes, preguntas y contraargumentos.",
            "Entrega checklist previo a la audiencia.",
            "No reemplaza la intervencion oral del abogado.",
        ],
    },
    {
        "id": "redactor_documentos_juridicos",
        "nombre_corto": "Redacción Documentos",
        "titulo_profesional": "REDACCIÓN DE ESCRITOS Y MEMORIALES PENALES",
        "proposito": "Convierte analisis juridico en escritos utilizables por el despacho.",
        "problema": "Reduce tiempo de redaccion y mejora estandar tecnico del primer borrador.",
        "necesidad": "Memoriales, solicitudes y recursos exigen estructura y soporte normativo preciso.",
        "no_reemplaza": "El criterio de firma y aprobacion de radicacion.",
        "prompt_simple": [
            "Redacta borradores de memoriales, solicitudes, ampliaciones y recursos.",
            "Estructura hechos, fundamentos y peticiones.",
            "Marca pendientes de verificacion.",
            "No inventa hechos, citas, radicados ni anexos.",
        ],
    },
    {
        "id": "analista_seguimiento_procesal",
        "nombre_corto": "Seguimiento Procesal",
        "titulo_profesional": "SEGUIMIENTO Y CONTROL DEL EXPEDIENTE PENAL",
        "proposito": "Monitorea estado de radicado, actuaciones, audiencias y terminos.",
        "problema": "Evita perdida de oportunidad por falta de control operativo.",
        "necesidad": "La trazabilidad procesal diaria impacta calidad de defensa de derechos de victima.",
        "no_reemplaza": "El analisis juridico estrategico.",
        "prompt_simple": [
            "Monitorea radicados, actuaciones y audiencias.",
            "Genera alertas de terminos y vencimientos.",
            "Produce reportes de estado del caso.",
            "Funcion operativa, no estrategica.",
        ],
    },
    {
        "id": "analista_calidad_juridica",
        "nombre_corto": "Control de Calidad Jurídica",
        "titulo_profesional": "REVISIÓN DE CALIDAD Y CONTROL DE RIESGOS JURÍDICOS",
        "proposito": "Revisa salida final antes de compartir externamente.",
        "problema": "Disminuye riesgo de alucinacion legal, inconsistencia estrategica y filtracion de datos sensibles.",
        "necesidad": "Refuerza responsabilidad profesional del despacho y soporte de auditoria interna.",
        "no_reemplaza": "La aprobacion final de quien representa.",
        "prompt_simple": [
            "Verifica soporte factico, citas normativas y coherencia estrategica.",
            "Controla confidencialidad y no revictimizacion.",
            "Clasifica si la salida es aprobable, requiere cambios o debe rechazarse.",
            "Nunca aprueba automaticamente sin marcar hallazgos.",
        ],
    },
]


def parse_skill_md_text(text: str) -> dict:
    """Parsea el cuerpo de un SKILL.md (texto completo)."""
    try:
        from src.config_store.service import strip_header

        text = strip_header(text or "")
    except Exception:
        pass
    body = text.split("---", 2)[-1] if text.startswith("---") else text

    def section(name: str) -> str:
        m = re.search(rf"## {re.escape(name)}[^\n]*\n(.*?)(?=\n## |\Z)", body, re.S)
        return m.group(1).strip() if m else ""

    agents_raw = section("Used By Agents")
    agents = re.findall(r"`([^`]+)`", agents_raw)
    tools_section = section("Tools")
    # Preferir solo function tools reales; ignorar Planned capabilities / Side-effects.
    ft = re.search(
        r"### Function tools[^\n]*\n(.*?)(?=\n### |\Z)",
        tools_section,
        re.S,
    )
    tools_src = ft.group(1) if ft else tools_section
    tools: list[str] = []
    for line in tools_src.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        for name in re.findall(r"`([^`]+)`", line):
            name = name.strip()
            if name and name not in tools:
                tools.append(name)
    guardrails = [g.strip("- ").strip() for g in section("Guardrails").splitlines() if g.strip().startswith("-")]
    category = ""
    cm = re.search(r"Category:\s*`([^`]+)`", body)
    if cm:
        category = cm.group(1)
    tier = ""
    tm = re.search(r"Tier:\s*`(\w+)`", body)
    if tm:
        tier = tm.group(1)

    steps_md: list[dict] = []
    for line in section("Steps").splitlines():
        sm = re.match(r"^\s*\d+\.\s+(.+)$", line.strip())
        if sm:
            steps_md.append({"text": sm.group(1).strip(), "modo": "serial"})

    rol_blocks = re.findall(r"## Rol en [^\n]+\n(.*?)(?=\n## |\Z)", body, re.S)
    rol = "\n\n".join(b.strip() for b in rol_blocks if b.strip())

    return {
        "purpose": section("Purpose"),
        "inputs": section("Inputs"),
        "outputs": section("Outputs"),
        "agents": agents,
        "tools": tools,
        "guardrails": guardrails,
        "category": category,
        "tier": tier,
        "rol": rol,
        "no_duplicar": section("No duplicar"),
        "handoff": section("Handoff"),
        "riesgo": section("Riesgo si se omite"),
        "steps_md": steps_md,
    }


def parse_skill_md(path: Path) -> dict:
    return parse_skill_md_text(path.read_text(encoding="utf-8"))


def parse_steps_from_content(content: str) -> list[dict]:
    """Extrae pasos con modo serial o paralelo desde bloque de skill en lista-aprobacion."""
    steps: list[dict] = []
    block_re = re.compile(
        r"  - Pasos(?: \((serie|paralelo[^)]*)\))?:\s*\n((?:[ \t]+\d+\..+(?:\n|$))+)",
        re.I | re.M,
    )
    blocks = list(block_re.finditer(content))
    if blocks:
        for m in blocks:
            label = (m.group(1) or "").lower()
            modo = "paralelo" if label.startswith("paralelo") else "serial"
            for sm in re.finditer(r"^\s*\d+\.\s+(.+)$", m.group(2), re.M):
                steps.append({"text": sm.group(1).strip(), "modo": modo})
        return steps
    plain = re.search(
        r"Pasos:\s*\n((?:[ \t]+\d+\..+(?:\n|$))+)",
        content,
        re.I,
    )
    if plain:
        for m in re.finditer(r"^\s*\d+\.\s+(.+)$", plain.group(1), re.M):
            steps.append({"text": m.group(1).strip(), "modo": "serial"})
    return steps


def parse_lista_steps() -> dict[str, dict]:
    text = LISTA.read_text(encoding="utf-8")
    result: dict[str, dict] = {}
    blocks = re.split(r"\n- `([^`]+)`\n", text)
    i = 1
    while i < len(blocks) - 1:
        skill_id = blocks[i]
        content = blocks[i + 1]
        i += 2
        instr = re.search(r"Instrucción tipo:\s*(.+)", content)
        steps = parse_steps_from_content(content)
        tools = re.search(r"Herramientas:\s*(.+)", content)
        agents_line = re.search(r"Agentes que lo usan:\s*(.+)", content)
        agents_list = re.findall(r"`([^`]+)`", agents_line.group(1)) if agents_line else []
        result[skill_id] = {
            "instruccion": instr.group(1).strip() if instr else "",
            "steps": steps,
            "tools_lista": tools.group(1).strip() if tools else "",
            "agents_lista": agents_list,
        }
    return result


def load_skills_catalog() -> dict[str, dict]:
    """Carga todos los skills desde SKILL.md y lista de aprobacion.

    Si hay versión activa en config_store (DB), esa versión sobrescribe el archivo.
    """
    lista = parse_lista_steps()
    skills: dict[str, dict] = {}
    for p in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        sid = p.parent.name
        data = parse_skill_md(p)
        # Siempre reportar ruta canónica agente/skills (aunque el loader use espejo).
        data["path"] = f"agente/skills/{sid}/SKILL.md"
        extra = lista.get(sid, {})
        data["instruccion"] = extra.get("instruccion", "")
        lista_steps = extra.get("steps", [])
        data["steps"] = lista_steps if lista_steps else data.get("steps_md", [])
        if extra.get("tools_lista") and not data.get("tools"):
            data["tools_lista"] = extra["tools_lista"]
        skills[sid] = data

    # Overlay desde config_store (DB autoritativa)
    try:
        from src.config_store import get_active_content
        from src.storage import get_repository

        for active in get_repository().list_config_active(kind="skill"):
            sid = active.key
            try:
                active_data = get_active_content("skill", sid)
            except Exception:
                continue
            content = (active_data.get("content") or "").strip()
            if not content:
                continue
            parsed = parse_skill_md_text(content)
            base = skills.get(sid, {})
            merged = {**base, **parsed}
            # Preferir canónico en disco; DB puede aún tener path .cursor legacy.
            disk = base.get("path") or f"agente/skills/{sid}/SKILL.md"
            db_path = (active_data.get("path") or "").replace("\\", "/")
            if db_path.startswith(".cursor/skills/"):
                db_path = "agente/skills/" + db_path.split("/", 2)[-1]
            merged["path"] = disk if disk.startswith("agente/skills/") else (db_path or disk)
            merged["config_version"] = active_data.get("version")
            merged["config_checksum"] = active_data.get("checksum")
            extra = lista.get(sid, {})
            if not merged.get("instruccion"):
                merged["instruccion"] = extra.get("instruccion", "")
            lista_steps = extra.get("steps", [])
            if lista_steps and not merged.get("steps"):
                merged["steps"] = lista_steps
            elif not merged.get("steps"):
                merged["steps"] = merged.get("steps_md", [])
            skills[sid] = merged
    except Exception:
        pass

    try:
        from lib.approved_skill_config import apply_approved_to_skills_raw

        skills = apply_approved_to_skills_raw(skills)
    except Exception:
        pass
    return skills


def agent_skills_map(skills: dict[str, dict]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {a["id"]: [] for a in AGENTS}
    for sid, data in skills.items():
        for agent in data.get("agents", []):
            if agent in mapping and sid not in mapping[agent]:
                mapping[agent].append(sid)
    return mapping


AGENT_GROUP_LABELS = {
    "coordinacion": "Coordinación",
    "especialista": "Especialistas",
    "calidad": "Control de calidad",
}

COORDINADOR_ID = "coordinador_caso"
CALIDAD_ID = "analista_calidad_juridica"


def agent_group(agent_id: str) -> str:
    if agent_id == COORDINADOR_ID:
        return "coordinacion"
    if agent_id == CALIDAD_ID:
        return "calidad"
    return "especialista"


CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "Skills de audiencias": "Preparación, guiones, solicitudes orales y riesgos en audiencias Ley 906.",
    "Skills de calidad juridica": "Control de alucinaciones, tono, confidencialidad y coherencia estratégica.",
    "Skills de evidencia y soporte probatorio": "Inventario probatorio, brechas, cadena de custodia y recaudo.",
    "Skills de hechos y cronologia": "Extracción factual, cronología, matrices hecho-fuente y vacíos.",
    "Skills de redaccion juridica penal": "Borradores de memoriales, solicitudes, recursos y piezas procesales.",
    "Skills de representacion de victimas": "Teoría del caso, derechos de la víctima y no revictimización.",
    "Skills de ruta procesal Ley 906": "Etapa procesal, oportunidades, términos y actuaciones de la víctima.",
    "Skills de seguimiento procesal": "Radicados, alertas de vencimiento y reportes operativos.",
    "Skills de tipicidad y responsabilidad penal": "Tipicidad preliminar, elementos del tipo y riesgos de atipicidad.",
    "Skills transversales": "Clasificación de tareas, urgencia y pendientes compartidos entre agentes.",
}


def build_skill_steps(raw_steps: list) -> list[dict]:
    out: list[dict] = []
    for i, item in enumerate(raw_steps, start=1):
        if isinstance(item, dict):
            text = (item.get("text") or "").strip()
            modo = item.get("modo") or "serial"
        else:
            text = str(item).strip()
            modo = "serial"
        if text:
            out.append({"num": len(out) + 1, "text": text, "modo": modo})
    return out


def agent_by_id(agent_id: str) -> dict | None:
    return next((a for a in AGENTS if a["id"] == agent_id), None)


def agent_titulo(agent_id: str) -> str:
    a = agent_by_id(agent_id)
    if a:
        return a.get("titulo_profesional") or AGENT_TITULOS.get(agent_id, agent_id)
    return agent_id


def infer_destinatario(agent_ids: list[str]) -> str:
    for aid in agent_ids:
        if aid in DESTINATARIO_BY_AGENT:
            return DESTINATARIO_BY_AGENT[aid]
    return "Despacho (revisión y uso profesional)"


def skill_flujo_pasos(steps: list[dict]) -> str:
    modos = {s.get("modo", "serial") for s in steps}
    if "paralelo" in modos:
        return "serie_y_paralelo"
    return "serial"


def skill_titulo_upper(instruccion: str, purpose: str = "") -> str:
    base = (instruccion or purpose or "").strip().rstrip(".")
    return base.upper() if base else ""


def _normalize_tool_name(value: str) -> str:
    return str(value).strip().strip("`").strip()


def skill_tools_list(data: dict) -> list[str]:
    """Herramientas del skill: SKILL.md Tools o fallback lista-aprobacion."""
    tools = [_normalize_tool_name(t) for t in (data.get("tools") or []) if _normalize_tool_name(t)]
    if tools:
        return tools
    lista = (data.get("tools_lista") or "").strip()
    if not lista or lista.lower() in ("sin_herramientas_obligatorias", "sin herramientas obligatorias"):
        return []
    parts = [p.strip() for p in lista.replace(",", " ").split() if p.strip()]
    return [_normalize_tool_name(p) for p in parts if _normalize_tool_name(p)]


def skill_tools_display(data: dict) -> str:
    tools = skill_tools_list(data)
    if tools:
        return ", ".join(f"`{t}`" for t in tools)
    return "Sin herramientas obligatorias declaradas."


def skill_guardrails_list(data: dict) -> list[str]:
    return [g.strip() for g in (data.get("guardrails") or []) if str(g).strip()]


def guia_audit_key(skill_id: str, part: str) -> str:
    return f"{skill_id}::{part}"

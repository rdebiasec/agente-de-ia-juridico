"""Catalogo compartido: agentes, guardrails y parsers de skills."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _resolve_skills_dir() -> Path:
    for candidate in (ROOT / ".cursor" / "skills", ROOT / "agente" / "skills"):
        if candidate.is_dir() and any(candidate.glob("*/SKILL.md")):
            return candidate
    return ROOT / ".cursor" / "skills"


SKILLS_DIR = _resolve_skills_dir()
LISTA = ROOT / "docs" / "canon" / "lista-aprobacion-agentes-skills-pasos.md"

GUARDRAILS = [
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
        "desc": "Escritos, estrategia, tutela y reportes a cliente requieren aprobacion.",
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

AGENT_TITULOS: dict[str, str] = {
    "coordinador_expediente_penal": "COORDINACIÓN Y ENRUTAMIENTO DEL CASO PENAL",
    "analista_cronologia_hechos_penales": "RECONSTRUCCIÓN CRONOLÓGICA DEL HECHO PENAL",
    "analista_tipicidad_y_responsabilidad_penal": "ANÁLISIS DE TIPICIDAD Y RESPONSABILIDAD PENAL",
    "analista_ruta_procesal_ley906": "ESTRATEGIA PROCESAL BAJO LA LEY 906 DE 2004",
    "analista_representacion_victimas": "REPRESENTACIÓN JURÍDICA CENTRADA EN LA VÍCTIMA",
    "gestor_evidencia_y_soporte_probatorio": "GESTIÓN PROBATORIA Y SOPORTE DE EVIDENCIA",
    "preparador_estrategico_audiencias_penales": "PREPARACIÓN ESTRATÉGICA DE AUDIENCIAS PENALES",
    "redactor_documentos_juridicos_penales": "REDACCIÓN DE ESCRITOS Y MEMORIALES PENALES",
    "gestor_seguimiento_procesal_penal": "SEGUIMIENTO Y CONTROL DEL EXPEDIENTE PENAL",
    "evaluador_derechos_fundamentales_tutela": "EVALUACIÓN DE TUTELA Y DERECHOS FUNDAMENTALES",
    "analista_calidad_juridica": "REVISIÓN DE CALIDAD Y CONTROL DE RIESGOS JURÍDICOS",
}

DESTINATARIO_BY_AGENT: dict[str, str] = {
    "coordinador_expediente_penal": "Siguiente agente o guía operativa del caso",
    "redactor_documentos_juridicos_penales": "Despacho (borrador para firma y radicación)",
    "analista_calidad_juridica": "Despacho (dictamen de conformidad)",
    "gestor_seguimiento_procesal_penal": "Despacho (alertas y estado del expediente)",
    "preparador_estrategico_audiencias_penales": "Despacho (insumos para audiencia)",
    "evaluador_derechos_fundamentales_tutela": "Despacho (evaluación constitucional preliminar)",
}

AGENTS = [
    {
        "id": "coordinador_expediente_penal",
        "nombre_corto": "Coordinador del expediente",
        "titulo_profesional": "COORDINACIÓN Y ENRUTAMIENTO DEL CASO PENAL",
        "proposito": "Recibe la consulta del despacho, entiende que necesita y la envia al especialista correcto.",
        "problema": "Evita perder tiempo en respuestas generales o mal enfocadas; ordena el trabajo por prioridad legal.",
        "necesidad": "En penal-victimas la estrategia cambia por etapa Ley 906; este coordinador reduce errores de enfoque.",
        "no_reemplaza": "El analisis de fondo por especialidad ni la aprobacion final.",
        "prompt_simple": [
            "Solo trabaja en casos de penal-victimas en Colombia.",
            "Decide a que especialista enviar cada consulta segun necesidad del caso.",
            "Si faltan datos importantes, primero los pide antes de dar una conclusion.",
            "No inventa normas, sentencias, radicados ni hechos.",
        ],
    },
    {
        "id": "analista_cronologia_hechos_penales",
        "nombre_corto": "Analista de cronologia y hechos",
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
        "id": "analista_tipicidad_y_responsabilidad_penal",
        "nombre_corto": "Analista de tipicidad y responsabilidad",
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
        "id": "analista_ruta_procesal_ley906",
        "nombre_corto": "Analista de ruta procesal Ley 906",
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
        "nombre_corto": "Analista de representacion de victimas",
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
        "id": "gestor_evidencia_y_soporte_probatorio",
        "nombre_corto": "Gestor de evidencia y prueba",
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
        "id": "preparador_estrategico_audiencias_penales",
        "nombre_corto": "Preparador de audiencias",
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
        "id": "redactor_documentos_juridicos_penales",
        "nombre_corto": "Redactor de documentos penales",
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
        "id": "gestor_seguimiento_procesal_penal",
        "nombre_corto": "Gestor de seguimiento procesal",
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
        "id": "evaluador_derechos_fundamentales_tutela",
        "nombre_corto": "Evaluador de tutela y derechos fundamentales",
        "titulo_profesional": "EVALUACIÓN DE TUTELA Y DERECHOS FUNDAMENTALES",
        "proposito": "Evalua si corresponde tutela o via alternativa, con criterio constitucional.",
        "problema": "Evita tutelas prematuras o improcedentes.",
        "necesidad": "En casos penales de victimas, tutela es excepcional y exige subsidiariedad e inmediatez.",
        "no_reemplaza": "La decision final de litigio constitucional del despacho.",
        "prompt_simple": [
            "Evalua derechos fundamentales afectados.",
            "Revisa subsidiariedad, inmediatez y perjuicio irremediable.",
            "Recomienda tutela o via alternativa.",
            "No convierte todo en tutela.",
        ],
    },
    {
        "id": "analista_calidad_juridica",
        "nombre_corto": "Analista de calidad juridica",
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


def parse_skill_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1] if text.startswith("---") else text

    def section(name: str) -> str:
        m = re.search(rf"## {re.escape(name)}[^\n]*\n(.*?)(?=\n## |\Z)", body, re.S)
        return m.group(1).strip() if m else ""

    agents_raw = section("Used By Agents")
    agents = re.findall(r"`([^`]+)`", agents_raw)
    tools = [t.strip("- ").strip() for t in section("Tools").splitlines() if t.strip().startswith("-")]
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
    """Carga todos los skills desde SKILL.md y lista de aprobacion."""
    lista = parse_lista_steps()
    skills: dict[str, dict] = {}
    for p in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        sid = p.parent.name
        data = parse_skill_md(p)
        rel = p.relative_to(ROOT).as_posix()
        data["path"] = rel
        extra = lista.get(sid, {})
        data["instruccion"] = extra.get("instruccion", "")
        lista_steps = extra.get("steps", [])
        data["steps"] = lista_steps if lista_steps else data.get("steps_md", [])
        if extra.get("tools_lista") and not data.get("tools"):
            data["tools_lista"] = extra["tools_lista"]
        skills[sid] = data
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

COORDINADOR_ID = "coordinador_expediente_penal"
CALIDAD_ID = "analista_calidad_juridica"


def agent_group(agent_id: str) -> str:
    if agent_id == COORDINADOR_ID:
        return "coordinacion"
    if agent_id == CALIDAD_ID:
        return "calidad"
    return "especialista"


CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "Skills constitucionales y tutela": "Tutela, subsidiariedad, inmediatez y derechos fundamentales.",
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

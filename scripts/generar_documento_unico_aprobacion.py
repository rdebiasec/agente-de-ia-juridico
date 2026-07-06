#!/usr/bin/env python3
"""Genera documento unico de aprobacion para la abogada (v1)."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import (  # noqa: E402
    AGENTS,
    agent_skills_map,
    load_skills_catalog,
)

OUT = ROOT / "docs" / "generados" / "documento-unico-aprobacion-abogada-penal-victimas.md"


def checklist_block(title: str) -> str:
    return f"""
**Checklist de aprobacion — {title}**

| Decision | Marcar |
|---|---|
| APROBAR | [ ] |
| AJUSTAR | [ ] |
| ELIMINAR | [ ] |
| PENDIENTE | [ ] |

**Observaciones / cambios sugeridos:**

> (espacio para la abogada)
"""


def main() -> None:
    skills = load_skills_catalog()
    agent_skills = agent_skills_map(skills)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []
    w = lines.append

    w("# Documento Unico de Aprobacion — Sistema Penal-Victimas (Colombia)")
    w("")
    w(f"**Version:** 1.0  ")
    w(f"**Fecha de generacion:** {now}  ")
    w("**Audiencia:** Abogada lider del despacho  ")
    w("**Proposito:** Revisar, aprobar o editar los 11 agentes, 90 skills y reglas del sistema en un solo lugar.")
    w("")
    w("---")
    w("")
    w("## Como usar este documento")
    w("")
    w("1. Lea primero las partes 1 a 7 para entender el sistema completo.")
    w("2. Revise cada agente en la parte 8 (hay 11).")
    w("3. Revise cada skill en la parte 9 (hay 90).")
    w("4. Valide flujos de conversacion en la parte 10.")
    w("5. Complete el checklist maestro en la parte 11.")
    w("6. Use la parte 12 si necesita cambiar prompts, skills o reglas.")
    w("")
    w("**Regla de oro:** La IA propone; la abogada revisa, ajusta y aprueba.")
    w("")
    w("---")
    w("")
    w("## Parte 0 — Resumen ejecutivo")
    w("")
    w("Este sistema tiene **11 agentes** y **90 skills** para apoyar la representacion de victimas en casos penales en Colombia.")
    w("")
    w("### Los 11 agentes")
    w("")
    for i, a in enumerate(AGENTS, 1):
        w(f"{i}. `{a['id']}` — {a['nombre_corto']}")
    w("")
    w("### Que hace el sistema")
    w("")
    w("- Ordena hechos y pruebas rapidamente.")
    w("- Ayuda a decidir la ruta procesal correcta bajo Ley 906.")
    w("- Produce borradores juridicos con trazabilidad.")
    w("- Controla riesgos: hechos sin soporte, citas no verificadas, tono revictimizante.")
    w("- Mantiene seguimiento de terminos y actuaciones.")
    w("")
    w("### Que NO hace el sistema")
    w("")
    w("- No reemplaza a la abogada.")
    w("- No firma ni radica documentos por cuenta propia.")
    w("- No atiende asuntos fuera de penal-victimas.")
    w("- No envia salidas externas sin revision humana.")
    w("")
    w(checklist_block("Resumen ejecutivo").strip())
    w("")
    w("---")
    w("")
    w("## Parte 1 — Por que estamos creando estos agentes")
    w("")
    w("- Para ahorrar tiempo en tareas repetitivas (ordenar hechos, revisar pruebas, preparar borradores).")
    w("- Para mantener una forma de trabajo consistente en todos los casos penales de victimas.")
    w("- Para reducir errores graves: hechos sin soporte, citas no verificadas o pasos fuera de tiempo.")
    w("- Para mejorar la preparacion de audiencias y escritos con informacion clara y ordenada.")
    w("- Para que la abogada tenga control final con revision humana antes de usar cualquier salida importante.")
    w("")
    w("## Parte 2 — Que valor aportan")
    w("")
    w("- **Mas productividad:** menos tiempo operativo y mas tiempo para estrategia legal.")
    w("- **Mas calidad:** mejores borradores iniciales y mejor trazabilidad de fuentes.")
    w("- **Menos riesgo:** controles para evitar inventar datos, normas o decisiones.")
    w("- **Mejor servicio a la victima:** respuestas mas claras y centradas en sus derechos.")
    w("")
    w("---")
    w("")
    w("## Parte 3 — Alcance y limites")
    w("")
    w("### Alcance habilitado")
    w("")
    w("- Jurisdiccion: Colombia.")
    w("- Materia: penal con enfoque en representacion de victimas.")
    w("- Marco principal: Ley 906 de 2004, Constitucion Politica y jurisprudencia aplicable.")
    w("")
    w("### Limites no negociables")
    w("")
    w("- El sistema no sustituye criterio profesional ni firma del abogado.")
    w("- No se inventan hechos, normas, sentencias, radicados ni autoridades.")
    w("- Toda salida externa requiere validacion humana.")
    w("- Los datos sensibles se tratan con minimizacion y confidencialidad.")
    w("- Si llega un asunto fuera de penal-victimas, el sistema lo declara fuera de alcance.")
    w("")
    w(checklist_block("Alcance y limites").strip())
    w("")
    w("---")
    w("")
    w("## Parte 4 — Arquitectura del sistema")
    w("")
    w("```mermaid")
    w("flowchart TD")
    w("  userConsulta[Consulta de la abogada] --> coordinator[coordinador_expediente_penal]")
    w("  coordinator --> hechos[analista_cronologia_hechos_penales]")
    w("  coordinator --> tipicidad[analista_tipicidad_y_responsabilidad_penal]")
    w("  coordinator --> ruta906[analista_ruta_procesal_ley906]")
    w("  coordinator --> victimas[analista_representacion_victimas]")
    w("  coordinator --> evidencia[gestor_evidencia_y_soporte_probatorio]")
    w("  coordinator --> audiencias[preparador_estrategico_audiencias_penales]")
    w("  coordinator --> redaccion[redactor_documentos_juridicos_penales]")
    w("  coordinator --> seguimiento[gestor_seguimiento_procesal_penal]")
    w("  coordinator --> tutela[evaluador_derechos_fundamentales_tutela]")
    w("  coordinator --> calidad[analista_calidad_juridica]")
    w("  calidad --> hitl[Revision humana de la abogada]")
    w("```")
    w("")
    w("### Lectura simple de la arquitectura")
    w("")
    w("1. La abogada hace una consulta.")
    w("2. El **coordinador** entiende que necesita y envia al especialista correcto.")
    w("3. El **especialista** trabaja con sus skills y produce un borrador o analisis.")
    w("4. El **analista de calidad** revisa antes de entregar.")
    w("5. La **abogada** aprueba, ajusta o rechaza.")
    w("")
    w(checklist_block("Arquitectura").strip())
    w("")
    w("---")
    w("")
    w("## Parte 5 — Reglas del sistema (guardrails)")
    w("")
    w("Estas reglas protegen la calidad juridica y la responsabilidad profesional:")
    w("")
    w("| Regla | Que significa en la practica |")
    w("|---|---|")
    w("| No inventar | Si no hay fuente verificada, se marca como pendiente de verificar |")
    w("| Pedir datos faltantes | Si faltan hechos, etapa o radicado, el sistema pregunta antes de concluir |")
    w("| Separar hecho de inferencia | Distingue lo confirmado, lo narrado y lo inferido |")
    w("| Revision humana obligatoria | Escritos, estrategia, tutela y reportes a cliente requieren aprobacion |")
    w("| No revictimizar | El lenguaje no culpa ni expone indebidamente a la victima |")
    w("| Confidencialidad | Detecta y controla datos sensibles innecesarios |")
    w("| Fuera de alcance | Consultas no penales se declaran fuera de alcance penal-victimas |")
    w("| Aviso de borrador | Toda respuesta termina con aviso de revision profesional |")
    w("")
    w("### Cuando se activa revision humana obligatoria")
    w("")
    w("Se activa cuando la consulta o respuesta involucra: redaccion, escritos, recursos, solicitudes, memoriales, tutela, estrategia, seguimiento, informes, radicacion, audiencias o entrevistas.")
    w("")
    w(checklist_block("Guardrails").strip())
    w("")
    w("---")
    w("")
    w("## Parte 6 — Base de conocimiento (fuentes internas)")
    w("")
    w("El sistema consulta solo estos archivos de conocimiento penal:")
    w("")
    w("| Archivo | Contenido esperado |")
    w("|---|---|")
    w("| `agente/conocimiento/penal.md` | Tipos penales, elementos, conceptos sustantivos |")
    w("| `agente/conocimiento/proceso-penal-906.md` | Etapas, actuaciones, terminos Ley 906 |")
    w("| `agente/conocimiento/normas-clave.md` | Normas constitucionales y legales de referencia |")
    w("")
    w("**Principio:** toda afirmacion juridica debe tener fuente verificable o marcarse como pendiente.")
    w("")
    w(checklist_block("Base de conocimiento RAG").strip())
    w("")
    w("---")
    w("")
    w("## Parte 7 — URLs oficiales y reputables")
    w("")
    w("### Normativa y vigencia")
    w("")
    w("- SUIN-Juriscol: https://www.suin-juriscol.gov.co/")
    w("- Ley 906 consolidada: http://www.secretariasenado.gov.co/senado/basedoc/ley_0906_2004.html")
    w("- Diario Oficial: https://svrpubindc.imprenta.gov.co/diario/index.xhtml")
    w("")
    w("### Jurisprudencia")
    w("")
    w("- Corte Constitucional — Relatoria: https://corteconstitucional.gov.co/relatoria/")
    w("- Corte Suprema — Sala Penal: https://cortesuprema.gov.co/sala-de-casacion-penal-relatoria/")
    w("- Consulta jurisprudencial (CENDOJ): https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml")
    w("")
    w("### Estado procesal y entidades")
    w("")
    w("- Consulta de procesos Rama Judicial: https://consultaprocesos.ramajudicial.gov.co/Procesos/Index")
    w("- Fiscalia General de la Nacion: https://www.fiscalia.gov.co/")
    w("- Instituto Nacional de Medicina Legal: https://www.medicinalegal.gov.co/")
    w("")
    w(checklist_block("URLs oficiales").strip())
    w("")
    w("---")
    w("")
    w("## Parte 8 — Los 11 agentes (detalle para aprobacion)")
    w("")

    for idx, agent in enumerate(AGENTS, 1):
        aid = agent["id"]
        w(f"### 8.{idx} `{aid}`")
        w("")
        w(f"**Nombre corto:** {agent['nombre_corto']}")
        w("")
        w(f"**Proposito:** {agent['proposito']}")
        w("")
        w(f"**Problema que resuelve:** {agent['problema']}")
        w("")
        w(f"**Por que es necesario en Colombia:** {agent['necesidad']}")
        w("")
        w(f"**No reemplaza:** {agent['no_reemplaza']}")
        w("")
        w("**Prompt del agente (lenguaje simple):**")
        w("")
        for p in agent["prompt_simple"]:
            w(f"- {p}")
        w("")
        skill_list = sorted(agent_skills.get(aid, []))
        w(f"**Skills asignados ({len(skill_list)}):**")
        w("")
        for sid in skill_list:
            w(f"- `{sid}` — ver seccion 9")
        w("")
        w(checklist_block(f"Agente {aid}").strip())
        w("")
        w("---")
        w("")

    w("## Parte 9 — Los 90 skills (ficha detallada)")
    w("")
    w("Cada skill es una capacidad atomica que un agente usa para una tarea especifica.")
    w("")

    by_category: dict[str, list[str]] = {}
    for sid, data in sorted(skills.items()):
        cat = data.get("category") or "Sin categoria"
        by_category.setdefault(cat, []).append(sid)

    skill_num = 0
    for cat in sorted(by_category):
        w(f"### Categoria: {cat}")
        w("")
        for sid in sorted(by_category[cat]):
            skill_num += 1
            data = skills[sid]
            w(f"#### 9.{skill_num} `{sid}`")
            w("")
            w(f"**Para que sirve:** {data.get('purpose') or data.get('instruccion', '')}")
            w("")
            w(f"**Archivo:** `{data['path']}`")
            w("")
            w(f"**Agentes que lo usan:** {', '.join(f'`{a}`' for a in data.get('agents', [])) or data.get('agents', 'N/D')}")
            w("")
            if data.get("instruccion"):
                w(f"**Instruccion tipo:** {data['instruccion']}")
                w("")
            w("**Que necesita para funcionar (entradas):**")
            w("")
            w(data.get("inputs") or "Depende del flujo. Solicitar datos faltantes antes de continuar.")
            w("")
            w("**Que produce (salidas):**")
            w("")
            w(data.get("outputs") or "Resultado estructurado para revision humana.")
            w("")
            w("**Pasos del skill:**")
            w("")
            steps = data.get("steps") or []
            if steps:
                for i, step in enumerate(steps, 1):
                    w(f"{i}. {step}")
            else:
                w("1. Recopilar informacion necesaria del caso.")
                w("2. Ejecutar la tarea segun su proposito.")
                w("3. Entregar resultado con fuentes y pendientes marcados.")
            w("")
            tools = data.get("tools") or []
            if isinstance(tools, str):
                tools_line = tools
            elif data.get("tools_lista"):
                tools_line = data["tools_lista"]
            else:
                tools_line = ", ".join(f"`{t}`" for t in tools) if tools else "Sin herramientas especificas"
            w(f"**Herramientas:** {tools_line}")
            w("")
            guardrails = data.get("guardrails") or []
            w("**Cuidados y riesgos:**")
            w("")
            if guardrails:
                for g in guardrails:
                    w(f"- {g}")
            else:
                w("- No inventar hechos ni fuentes. Requiere revision humana.")
            w("")
            w(checklist_block(f"Skill {sid}").strip())
            w("")

    w("---")
    w("")
    w("## Parte 10 — Flujos de conversacion (ejemplos para aprobacion)")
    w("")
    w("### 10.1 Flujo completo (todos los agentes)")
    w("")
    w("**Caso tipo:** macrocaso con hechos extensos, multiples pruebas, audiencia proxima y posible tutela.")
    w("")
    w("```mermaid")
    w("flowchart LR")
    w("  A[Ingreso] --> B[Coordinador]")
    w("  B --> C[Cronologia]")
    w("  C --> D[Tipicidad]")
    w("  D --> E[Ruta 906]")
    w("  E --> F[Representacion victimas]")
    w("  F --> G[Evidencia]")
    w("  G --> H[Audiencias]")
    w("  H --> I[Redaccion]")
    w("  I --> J[Seguimiento]")
    w("  J --> K[Tutela]")
    w("  K --> L[Calidad]")
    w("  L --> M[Abogada aprueba]")
    w("```")
    w("")
    flows = [
        (
            "10.2 Ampliacion de denuncia",
            "coordinador -> cronologia -> evidencia -> redaccion -> calidad",
            "Tengo nuevos hechos y anexos; necesito ampliar denuncia.",
            [
                "Ordena hechos por fecha",
                "Vincula cada hecho a su fuente",
                "Arma borrador de ampliacion",
                "Pasa control de calidad y queda pendiente de aprobacion humana",
            ],
        ),
        (
            "10.3 Preparacion de audiencia",
            "coordinador -> ruta906 -> audiencias -> calidad",
            "Tengo audiencia en 48 horas; necesito objetivo, solicitudes y guion.",
            [
                "Valida etapa procesal",
                "Propone objetivo juridico",
                "Construye checklist, guion y contraargumentos",
                "Revisa riesgo de tono y soporte de citas",
            ],
        ),
        (
            "10.4 Seguimiento de radicado",
            "coordinador -> seguimiento -> calidad",
            "Dame estado de radicado y alertas de vencimiento de esta semana.",
            [
                "Resume actuaciones recientes",
                "Alerta terminos relevantes",
                "Produce resumen operativo para cliente sin estrategia sensible",
            ],
        ),
        (
            "10.5 Tutela por inaccion institucional",
            "coordinador -> tutela -> redaccion -> calidad",
            "Fiscalia no responde; evaluar tutela y borrador.",
            [
                "Revisa subsidiariedad e inmediatez",
                "Identifica derecho afectado y perjuicio",
                "Sugiere tutela o via alternativa",
                "Si procede, entrega borrador preliminar para revision humana",
            ],
        ),
        (
            "10.6 Memorial de impulso procesal",
            "redaccion -> calidad",
            "Prepare memorial de impulso procesal por inactividad, con solicitud concreta.",
            [
                "Estructura hechos, fundamentos y peticiones",
                "Verifica citas normativas",
                "Marca pendientes de validacion",
            ],
        ),
    ]
    for title, agents_chain, ejemplo, pasos in flows:
        w(f"### {title}")
        w("")
        w(f"**Agentes:** {agents_chain}")
        w("")
        w(f"**Ejemplo de consulta:** \"{ejemplo}\"")
        w("")
        w("**Que hace el sistema:**")
        w("")
        for i, p in enumerate(pasos, 1):
            w(f"{i}. {p}")
        w("")
        w(checklist_block(title).strip())
        w("")

    w("---")
    w("")
    w("## Parte 11 — Checklist maestro de aprobacion")
    w("")
    w("### 11.1 Agentes (11)")
    w("")
    w("| # | Agente | APROBAR | AJUSTAR | ELIMINAR | PENDIENTE | Observaciones |")
    w("|---|---|---|---|---|---|---|")
    for i, a in enumerate(AGENTS, 1):
        w(f"| {i} | `{a['id']}` | [ ] | [ ] | [ ] | [ ] | |")
    w("")
    w("### 11.2 Skills (90)")
    w("")
    w("| # | Skill | Agente principal | APROBAR | AJUSTAR | ELIMINAR | PENDIENTE |")
    w("|---|---|---|---|---|---|---|")
    for i, sid in enumerate(sorted(skills), 1):
        agents_for_skill = skills[sid].get("agents", [])
        primary = agents_for_skill[0] if agents_for_skill else "N/D"
        w(f"| {i} | `{sid}` | `{primary}` | [ ] | [ ] | [ ] | [ ] |")
    w("")
    w("### 11.3 Reglas del sistema")
    w("")
    w("| Regla | APROBAR | AJUSTAR | ELIMINAR | PENDIENTE |")
    w("|---|---|---|---|---|")
    for regla in [
        "No inventar hechos ni normas",
        "Revision humana en salidas externas",
        "No revictimizacion",
        "Confidencialidad de datos sensibles",
        "Fuera de alcance penal-victimas",
        "Aviso de borrador obligatorio",
    ]:
        w(f"| {regla} | [ ] | [ ] | [ ] | [ ] |")
    w("")
    w("### 11.4 Base de conocimiento y URLs")
    w("")
    w("| Elemento | APROBAR | AJUSTAR | PENDIENTE |")
    w("|---|---|---|---|")
    for item in [
        "penal.md",
        "proceso-penal-906.md",
        "normas-clave.md",
        "URLs normativas",
        "URLs jurisprudencia",
        "URLs estado procesal",
    ]:
        w(f"| {item} | [ ] | [ ] | [ ] |")
    w("")
    w("### 11.5 Flujos de conversacion")
    w("")
    w("| Flujo | APROBAR | AJUSTAR | PENDIENTE |")
    w("|---|---|---|---|")
    for f in [
        "Flujo completo",
        "Ampliacion de denuncia",
        "Preparacion de audiencia",
        "Seguimiento de radicado",
        "Tutela por inaccion",
        "Memorial de impulso",
    ]:
        w(f"| {f} | [ ] | [ ] | [ ] |")
    w("")
    w("### 11.6 Campos de ajuste recomendados")
    w("")
    w("- Nivel de formalidad del lenguaje: ___________________________")
    w("- Profundidad de analisis por tipo de caso: ___________________________")
    w("- Evidencia minima exigida por salida: ___________________________")
    w("- Politica de escalamiento a revision humana: ___________________________")
    w("- Fuentes permitidas por tipo de escrito: ___________________________")
    w("")
    w("### 11.7 Decision final de la abogada")
    w("")
    w("- [ ] Aprobar sistema completo")
    w("- [ ] Aprobar con ajustes (detallar en observaciones)")
    w("- [ ] No aprobar (detallar motivos)")
    w("")
    w("**Firma / fecha:** ___________________________")
    w("")
    w("---")
    w("")
    w("## Parte 12 — Como editar el sistema")
    w("")
    w("| Si quiere cambiar... | Edite este archivo |")
    w("|---|---|")
    w("| Reglas comunes de todos los agentes | `agente/prompts/sistema.md` |")
    w("| Comportamiento de un agente especifico | `src/agents/orchestrator.py` |")
    w("| Un skill (pasos, entradas, salidas) | `agente/skills/<nombre>/SKILL.md` |")
    w("| Reglas de revision humana | `src/agents/guardrails.py` |")
    w("| Archivos de conocimiento penal | `agente/conocimiento/*.md` |")
    w("")
    w("### Orden sugerido de revision por skill")
    w("")
    w("1. Proposito — ¿tiene sentido para la practica del despacho?")
    w("2. Pasos — ¿son los pasos que haria un abogado humano?")
    w("3. Salida esperada — ¿es util y completa?")
    w("4. Cuidados — ¿protegen bien a la victima y al despacho?")
    w("")
    w("---")
    w("")
    w("## Documentos de respaldo (no borrar)")
    w("")
    w("- `docs/archive/entrega-md-razones-valor-agentes-skills-pasos.md`")
    w("- `docs/archive/reporte-maestro-revision-abogada-penal-victimas.md`")
    w("- `docs/canon/guia-aprobacion-abogada-flujos-penal-victimas.md`")
    w("- `docs/canon/lista-aprobacion-agentes-skills-pasos.md`")
    w("")
    w(f"*Generado automaticamente desde codigo y skills — {now}*")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: {OUT} ({len(lines)} lineas, {len(skills)} skills, {len(AGENTS)} agentes)")


if __name__ == "__main__":
    main()

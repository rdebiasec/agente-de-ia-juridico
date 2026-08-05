<!-- config-version: 2; checksum: 95b13cbacf799d43 -->
---
name: preparar-guion-intervencion-oral
description: Contrato penal-víctimas: Armar guion breve de intervención oral del abogado de la víctima: apertura, argumento, réplicas y cierre con peticiones. Activar cuando el plan/HITL o el especialista requiera `preparar_guion_intervencion_oral`. No sustituye a `preparar_preguntas_audie...
disable-model-invocation: true
---

# preparar_guion_intervencion_oral

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_guion_intervencion_oral`
- Tier: `critico`

## Used By Agents
- `analista_audiencias` (skill crítico de intervención oral)

## Purpose
Armar guion breve de intervención oral del abogado de la víctima: apertura, argumento, réplicas y cierre con peticiones.

## Rol en analista_audiencias
Producto táctico para audiencia; requiere `identificar_objetivo_audiencia` y hechos soportados.

## Inputs
- Objetivo jurídico y táctico (`identificar_objetivo_audiencia`).
- Cronología verificada y matriz hecho-prueba.
- Tipo de audiencia, etapa Ley 906 y tiempo estimado de intervención.
- Contraargumentos anticipados (`preparar_contraargumentos`, si existe).

## Outputs
- Guion por bloques: `apertura`, `nucleo_argumentativo`, `replicas_criticas`, `cierre_peticiones`.
- Tiempo estimado por bloque (minutos).
- Frases marcadas `REVISAR_TONO` si riesgo de revictimización.
- Etiqueta: `GUION PRELIMINAR — ENSAYAR CON ABOGADO ANTES DE AUDIENCIA`.

## Steps
1. Ordenar puntos orales alineados a objetivos y hechos soportados.
2. Incluir solicitudes y respuestas a objeciones previsibles.
3. Marcar datos no verificados; no inventar jurisprudencia oral.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `preparar_guion_intervencion_oral`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `hearing_template_loader` — no implementada
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar hechos ni normas en el argumento oral.
- **Separar hecho de inferencia:** Distinguir hechos soportados de hipótesis tácticas.
- **Revision humana obligatoria:** HITL obligatorio; no usar guion sin ensayo del abogado.
- **No revictimizar:** Lenguaje respetuoso; no exponer detalles gráficos innecesarios.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No listar preguntas a testigos (`preparar_preguntas_audiencia`).
- No simular escenarios (`simular_escenarios_audiencia`).
- No definir objetivo (`identificar_objetivo_audiencia`).

## Riesgo si se omite
Intervención oral improvisada, con argumentos no soportados o que revictimizan a quien representamos.

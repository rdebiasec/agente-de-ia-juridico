---
name: preparar-guion-intervencion-oral
description: Skill critico penal-victimas: estructurar intervencion oral clara y breve. Use when the workflow requires `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# preparar_guion_intervencion_oral

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_guion_intervencion_oral`
- Tier: `critico`

## Used By Agents
- `preparador_estrategico_audiencias_penales` (skill crítico de intervención oral)

## Purpose
Armar guion breve de intervención oral del abogado de la víctima: apertura, argumento, réplicas y cierre con peticiones.

## Rol en preparador_estrategico_audiencias_penales
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
1. Definir objetivo jurídico y táctico de la intervención en audiencia.
2. Ubicar etapa procesal y norma Ley 906 que habilita la intervención.
3. Estructurar apertura breve con postura de la víctima.
4. Desarrollar núcleo argumentativo solo con hechos soportados.
5. Anticipar réplicas a defensa y Fiscalía en puntos críticos.
6. Revisar lenguaje para evitar revictimización y filtración de estrategia.
7. Cerrar con peticiones concretas alineadas al objetivo de audiencia.
8. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `hearing_template_loader`
- `rag_ley906_search`

## Guardrails (g1–g10)
- **g1:** No inventar hechos ni normas en el argumento oral.
- **g3:** Distinguir hechos soportados de hipótesis tácticas.
- **g4:** HITL obligatorio; no usar guion sin ensayo del abogado.
- **g5:** Lenguaje respetuoso; no exponer detalles gráficos innecesarios.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No listar preguntas a testigos (`preparar_preguntas_audiencia`).
- No simular escenarios (`simular_escenarios_audiencia`).
- No definir objetivo (`identificar_objetivo_audiencia`).

## Riesgo si se omite
Intervención oral improvisada, con argumentos no soportados o que revictimizan a quien representamos.

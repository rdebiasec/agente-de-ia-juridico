---
name: generar-preguntas-testigos-peritos
description: Skill atomico penal-victimas: preparar preguntas neutrales para testigos o peritos. Use when the workflow requires `generar_preguntas_testigos_peritos`.
disable-model-invocation: true
---

# generar_preguntas_testigos_peritos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `generar_preguntas_testigos_peritos`
- Tier: `operativo`

## Used By Agents
- `preparador_estrategico_audiencias_penales`
- `analista_cronologia_hechos_penales`

## Purpose
Formular preguntas para testigos o peritos (no para la víctima) alineadas a hechos pendientes de aclarar.

## Rol en preparador_estrategico_audiencias_penales
Uso principal en preparación de audiencia.

## Rol en analista_cronologia_hechos_penales
Solo para aclarar huecos factuales vía terceros; no preguntas a víctima.

## Inputs
- Matriz hecho-prueba y vacíos factuales.
- Tipo de testigo/perito y objeto de su declaración.
- Objetivo probatorio por bloque.

## Outputs
- Preguntas: `destinatario` (testigo | perito), `pregunta`, `hecho_que_aclara`, `riesgo` (bajo | medio).
- Etiqueta: `PREGUNTAS TERCEROS — NO VÍCTIMA`.

## Steps
1. Identificar hechos que requieren aclaración por testigo o perito.
2. Formular preguntas neutrales y no inductivas.
3. Ordenar por relevancia probatoria.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g4:** HITL antes de audiencia.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No preguntas a víctima (`preparar_preguntas_audiencia`).
- No preguntas de tipicidad (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Pérdida de oportunidad para cerrar huecos factuales con testigos clave.

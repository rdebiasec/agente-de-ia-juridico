<!-- config-version: 3; checksum: 34ba0d85a1962a35 -->
---
name: generar-preguntas-testigos-peritos
description: Contrato penal-víctimas: Formular preguntas para testigos o peritos (no para la víctima) alineadas a hechos pendientes de aclarar. Activar cuando el plan/HITL o el especialista requiera `generar_preguntas_testigos_peritos`. No sustituye a `preparar_preguntas_audiencia`.
disable-model-invocation: true
---

# generar_preguntas_testigos_peritos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `generar_preguntas_testigos_peritos`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias`
- `analista_cronologia_hechos`

## Purpose
Formular preguntas para testigos o peritos (no para la víctima) alineadas a hechos pendientes de aclarar.

## Rol en analista_audiencias
Uso principal en preparación de audiencia.

## Rol en analista_cronologia_hechos
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
Skills = contratos (no function_tools invocables). No existe tool LLM `generar_preguntas_testigos_peritos`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **Revision humana obligatoria:** HITL antes de audiencia.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No preguntas a víctima (`preparar_preguntas_audiencia`).
- No preguntas de tipicidad (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Pérdida de oportunidad para cerrar huecos factuales con testigos clave.

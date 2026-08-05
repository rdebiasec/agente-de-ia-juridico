<!-- config-version: 2; checksum: 3da08213d54edf1c -->
---
name: preparar-contraargumentos
description: Contrato penal-víctimas: Anticipar argumentos de defensa o Fiscalía y preparar réplicas para audiencia o memorial. Activar cuando el plan/HITL o el especialista requiera `preparar_contraargumentos`. No sustituye a `preparar_guion_intervencion_oral`.
disable-model-invocation: true
---

# preparar_contraargumentos

## Scope
- Category: `Skills de audiencias`
- Skill ID: `preparar_contraargumentos`
- Tier: `operativo`

## Used By Agents
- `analista_audiencias`

## Purpose
Anticipar argumentos de defensa o Fiscalía y preparar réplicas para audiencia o memorial.

## Rol en analista_audiencias
Réplicas anticipadas para audiencia o memorial; insumo estratégico, no conclusión.
## Inputs
- Teoría del caso contraria (hipótesis documentada).
- Prueba disponible y matriz hecho-prueba.
- Tipo de audiencia u escrito objetivo.

## Outputs
- `contraargumentos`: argumento_ajeno | réplica_sugerida | prueba_de_apoyo | riesgo.
- Etiqueta: `HIPÓTESIS TÁCTICA — NO AFIRMAR HECHOS NO PROBADOS`.

## Steps
1. Identificar líneas argumentativas probables de la contraparte.
2. Preparar réplicas con hechos soportados y norma aplicable.
3. Señalar puntos débiles de la réplica que requieren prueba adicional.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `preparar_contraargumentos`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_ley906_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **Separar hecho de inferencia:** Réplicas basadas en hechos soportados, no en especulación.
- **Revision humana obligatoria:** HITL obligatorio antes de usar en audiencia o memorial.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No guion oral (`preparar_guion_intervencion_oral`).
- No simulación (`simular_escenarios_audiencia`).

## Riesgo si se omite
Improvisación ante argumentos previsibles de defensa o Fiscalía.

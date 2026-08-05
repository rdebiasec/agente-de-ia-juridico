<!-- config-version: 6; checksum: d2ee1341f240e3a1 -->
---
name: marcar-pendientes-verificacion
description: Contrato penal-víctimas: Recorrer la salida del turno e insertar `[PENDIENTE DE VERIFICAR]` en todo dato, cita normativa, hecho o radicado sin fuente verificable. Activar cuando el plan/HITL o el especialista requiera `marcar_pendientes_verificacion`. No sustituye a `verificar...
disable-model-invocation: true
---

# marcar_pendientes_verificacion

## Scope
- Category: `Skills transversales`
- Skill ID: `marcar_pendientes_verificacion`
- Tier: `atomico`

## Index Blurb
Etiqueta todo dato no verificado antes de entregar la voz del despacho.

## Used By Agents
- `coordinador_caso`

## Purpose
Recorrer la salida del turno e insertar `[PENDIENTE DE VERIFICAR]` en todo dato, cita normativa, hecho o radicado sin fuente verificable.

## Rol en coordinador_caso
Control de calidad transversal antes de entregar cualquier salida del coordinador o de ensamblar respuestas de subagentes. Persistencia estructurada vía `record_specialist_result`.

## Inputs
- Texto o estructura de salida a revisar (del turno actual o borrador consolidado).
- Fuentes disponibles en expediente o RAG para contrastar.
- Lista opcional de elementos ya marcados por otros skills.

## Outputs
- Texto con marcadores `[PENDIENTE DE VERIFICAR]` insertados.
- Registro de pendientes: `elemento`, `tipo` (`hecho` | `cita` | `radicado` | `fecha` | `otro`), `impacto_juridico` (`alto` | `medio` | `bajo`).
- En ledger: tareas `verificacion_especialista` con `pendiente_tipo` e `impacto_juridico`.
- Conteo de pendientes y recomendación de no uso externo si hay impacto alto.

## Steps
1. Recorrer salida/borrador y listar afirmaciones sin soporte.
2. Etiquetar con `[PENDIENTE DE VERIFICAR]` y dueño sugerido.
3. No corregir el fondo jurídico ni aprobar calidad.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `marcar_pendientes_*`.

### Function tools (LLM)
- (ninguna específica de este skill)

### Side-effects de código (no son function_tools)
- `audit_trace` — marcadores en síntesis del Gerente y post-validación
- `record_specialist_result` — parsea `[PENDIENTE DE VERIFICAR]` / `[FALTANTE]` y persiste `pendiente_tipo` + `impacto_juridico` en `tareas_gerencia`

## Guardrails
- **No inventar:** Implementación directa de g1 — todo sin fuente queda marcado, nunca inventado.
- **Separar hecho de inferencia:** No eliminar la distinción hecho/inferencia al marcar; solo etiquetar.
- **Revision humana obligatoria:** Si impacto alto (etapa, memorial, término), bloquear uso externo hasta revisión humana.
- **Aviso de borrador:** Incluir aviso estándar de revisión profesional al final.

## Handoff
- Impacto alto → retener en despacho / HITL antes de uso externo.
- Impacto medio/bajo → entregar con marcadores visibles al abogado.

## No duplicar
- No validar existencia de normas (`verificar_citas_normativas` → calidad/redactor).
- No cruzar hechos con expediente en profundidad (`verificar_hechos_soportados`).
- No clasificar tipo de fuente (`clasificar_fuente_factual`).

## Best Practices
- Preferir sobre-marcar a afirmar sin soporte.
- No borrar el contenido dudoso: marcar y dejar visible.

## Riesgo si se omite
Uso de afirmaciones sin soporte en comunicaciones del despacho → responsabilidad profesional y daño al caso.

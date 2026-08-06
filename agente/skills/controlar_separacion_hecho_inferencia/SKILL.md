<!-- config-version: 3; checksum: 790b41c0c3af76b8 -->
---
name: controlar-separacion-hecho-inferencia
description: Contrato penal-víctimas: Verificar que hechos confirmados, narrados, inferidos y pendientes estén claramente separados en la salida. Activar cuando el plan/HITL o el especialista requiera `controlar_separacion_hecho_inferencia`. No sustituye a `verificar_hechos_soportados`.
disable-model-invocation: true
---

# controlar_separacion_hecho_inferencia

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_separacion_hecho_inferencia`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`
- `analista_calidad_juridica`

## Purpose
Verificar que hechos confirmados, narrados, inferidos y pendientes estén claramente separados en la salida.

## Rol en redactor_documentos_juridicos
Autocontrol antes de entregar borrador.

## Rol en analista_calidad_juridica
Control de calidad en documentos para uso externo.

## Fuentes KB
- Relato/expediente y matriz hecho-fuente del caso; no inventar soporte.
- `agente/conocimiento/proceso-penal-906.md` — separar hecho/inferencia en piezas revisables.
- `agente/conocimiento/normas-clave.md` — no presentar sospechas como hechos; HITL antes de memorial.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento` para anclar afirmaciones.

## Inputs
- Texto del memorial, petición o análisis.
- Matriz hecho-fuente o cronología (si existe).

## Outputs
- `fragmentos`: texto | clasificación (confirmado | narrado | inferido | pendiente) | observación.
- `correcciones_sugeridas` para separar hecho de argumentación.
- Etiqueta: `CONTROL HECHO-INFERENCIA`.

## Steps
1. Identificar afirmaciones fácticas en el texto.
2. Clasificar cada una según soporte documental.
3. Señalar mezclas de hecho con inferencia o calificación penal.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_separacion_hecho_inferencia`.

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
- **Separar hecho de inferencia:** No reclasificar hecho confirmado sin fuente.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No verificar soporte global (`verificar_hechos_soportados`).
- No redactar hechos (`extraer_hechos_relevantes`).

## Riesgo si se omite
Memorial que presenta inferencias o sospechas como hechos probados ante el juez.

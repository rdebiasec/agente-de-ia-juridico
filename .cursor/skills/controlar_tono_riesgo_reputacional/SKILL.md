---
name: controlar-tono-riesgo-reputacional
description: Skill atomico penal-victimas: revisar tono profesional y evitar lenguaje riesgoso. Use when the workflow requires `controlar_tono_riesgo_reputacional`.
disable-model-invocation: true
---

# controlar_tono_riesgo_reputacional

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_riesgo_reputacional`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos_penales`
- `analista_calidad_juridica`

## Purpose
Detectar contenido que exponga al despacho o a la víctima a riesgo reputacional o mediático innecesario.

## Rol en redactor_documentos_juridicos_penales
Filtro antes de radicar o comunicar.

## Rol en analista_calidad_juridica
Control en comunicaciones sensibles.

## Inputs
- Texto destinado a terceros (cliente, prensa, redes, contraparte no procesal).
- Contexto del caso y perfil público de las partes.

## Outputs
- `riesgos_reputacionales`: exposición_mediática | dato_sensible | acusación_pública | ok.
- `mitigaciones` recomendadas.
- Etiqueta: `SOLO_ABOGADO` si hay riesgo alto.

## Steps
1. Identificar afirmaciones que puedan generar exposición pública indebida.
2. Evaluar si el riesgo es necesario para la estrategia procesal.
3. Proponer redacción más reservada cuando sea posible.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_tono_riesgo_reputacional`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

## Guardrails (g1–g10)
- **g6:** No amplificar datos sensibles en comunicaciones.
- **g4:** HITL obligatorio antes de comunicación externa.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No tono judicial (`controlar_tono_juridico_documento`).
- No resumen al cliente (`preparar_resumen_operativo_cliente`).

## Riesgo si se omite
Daño reputacional al despacho o a la víctima por comunicación imprudente.

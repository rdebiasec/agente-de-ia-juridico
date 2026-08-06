<!-- config-version: 4; checksum: 1409ad7b0d05fe96 -->
---
name: controlar-tono-riesgo-reputacional
description: Contrato penal-víctimas: Detectar contenido que exponga al despacho o a la víctima a riesgo reputacional o mediático innecesario. Activar cuando el plan/HITL o el especialista requiera `controlar_tono_riesgo_reputacional`. No sustituye a `controlar_tono_juridico_documento`.
disable-model-invocation: true
---

# controlar_tono_riesgo_reputacional

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_tono_riesgo_reputacional`
- Tier: `operativo`

## Used By Agents
- `redactor_documentos_juridicos`
- `analista_calidad_juridica`

## Purpose
Detectar contenido que exponga al despacho o a la víctima a riesgo reputacional o mediático innecesario.

## Rol en redactor_documentos_juridicos
Filtro antes de radicar o comunicar.

## Rol en analista_calidad_juridica
Control en comunicaciones sensibles.

## Fuentes KB
- `agente/conocimiento/normas-clave.md` — dignidad víctima; checklist calidad/citas.
- `agente/conocimiento/proceso-penal-906.md` — salida revisable; no comunicación pública sin HITL.
- Tools reales: `buscar_en_expediente` / `buscar_en_conocimiento` si el riesgo depende de dato del caso.
- Riesgo alto → etiqueta `SOLO_ABOGADO`; no amplificar datos sensibles.

## Inputs
- Texto destinado a terceros (cliente, prensa, redes, contraparte no procesal).
- Contexto del caso y perfil público de las partes.

## Outputs
- `riesgos_reputacionales`: exposición_mediática | dato_sensible | acusación_pública | ok.
- `mitigaciones` recomendadas.
- Etiqueta: `SOLO_ABOGADO` si hay riesgo alto.

## Steps
0. Evaluar exposicion vs necesidad procesal; anclar a Fuentes KB; riesgo alto → SOLO_ABOGADO.
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

## Guardrails
- **Confidencialidad:** No amplificar datos sensibles en comunicaciones.
- **Revision humana obligatoria:** HITL obligatorio antes de comunicación externa.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No tono judicial (`controlar_tono_juridico_documento`).
- No resumen al cliente (`preparar_resumen_operativo_cliente`).

## Riesgo si se omite
Daño reputacional al despacho o a la víctima por comunicación imprudente.

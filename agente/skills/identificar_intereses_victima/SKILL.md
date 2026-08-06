<!-- config-version: 3; checksum: d3ddf1a45f1e49a9 -->
---
name: identificar-intereses-victima
description: Contrato penal-víctimas: Identificar intereses y expectativas de la víctima en el proceso (reparación, verdad, seguridad, celeridad, etc.). Activar cuando el plan/HITL o el especialista requiera `identificar_intereses_victima`. No sustituye a `analizar_derechos_victima`.
disable-model-invocation: true
---

# identificar_intereses_victima

## Scope
- Category: `Skills de representacion de victimas`
- Skill ID: `identificar_intereses_victima`
- Tier: `operativo`

## Used By Agents
- `analista_representacion_victimas`

## Purpose
Identificar intereses y expectativas de la víctima en el proceso (reparación, verdad, seguridad, celeridad, etc.).

## Rol en analista_representacion_victimas
Traduce hechos y contexto en objetivos de representación centrada en la víctima.
## Inputs
- Relato o declaración de la víctima (si consta).
- Notas del abogado sobre objetivos del cliente.
- Etapa procesal y opciones disponibles.

## Outputs
- `intereses`: lista priorizada con fuente (declarada | inferida_documentada | pendiente).
- `tensiones` entre intereses si las hay.
- Etiqueta: `INTERVIEW HITL — NO SUSTITUYE DECISIÓN ABOGADO`.

## Steps
1. Recopilar intereses expresados por la víctima o documentados.
2. Clasificar y priorizar sin imponer objetivos ajenos.
3. Señalar intereses que requieren confirmación con la víctima.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_intereses_victima`.

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
- **Pedir datos faltantes:** Sin input de la víctima, marcar pendiente; no inventar intereses.
- **No revictimizar:** No presionar objetivos que revictimicen.
- **Revision humana obligatoria:** HITL obligatorio.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No derechos procesales (`analizar_derechos_victima`).
- No teoría del caso (`construir_teoria_caso_victima`).

## Riesgo si se omite
Representación que persigue metas procesales ajenas a lo que la víctima necesita.

---
name: identificar-intereses-victima
description: Skill atomico penal-victimas: aclarar el objetivo real de la victima. Use when the workflow requires `identificar_intereses_victima`.
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


## Rol en representacion_victima
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
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g2:** Sin input de la víctima, marcar pendiente; no inventar intereses.
- **g5:** No presionar objetivos que revictimicen.
- **g4:** HITL obligatorio.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No derechos procesales (`analizar_derechos_victima`).
- No teoría del caso (`construir_teoria_caso_victima`).

## Riesgo si se omite
Representación que persigue metas procesales ajenas a lo que la víctima necesita.

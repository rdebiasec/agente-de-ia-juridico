---
name: identificar-actores-y-roles
description: Skill operativo penal-victimas: identificar victima, presunto responsable, testigos, autoridades, terceros y entidades. Use when the workflow requires `identificar_actores_y_roles`.
disable-model-invocation: true
---

# identificar_actores_y_roles

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `identificar_actores_y_roles`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos_penales`
- `analista_representacion_victimas`

## Purpose
Extraer personas y entidades mencionadas en las fuentes y asignar rol procesal preliminar.

## Rol en analista_cronologia
Ejecutar en paralelo o justo después de `extraer_hechos_relevantes`. Alimenta cronología y detección de contradicciones.

## Inputs
- Hechos extraídos y documentos del expediente.
- Denuncia, informes de policía, actuaciones procesales (si existen).
- Nombres, alias, cargos y entidades mencionados en el turno.

## Outputs
- Mapa: `nombre_o_referencia`, `rol_preliminar` (víctima | indiciado/imputado | testigo | autoridad | tercero | entidad), `fuente`, `relevancia`, `datos_sensibles` (sí/no).
- Actores sin rol claro marcados `[PENDIENTE DE VERIFICAR]`.
- Alertas PII para control de confidencialidad.

## Steps
1. Extraer personas y entidades mencionadas en las fuentes.
2. Asignar rol procesal preliminar (víctima, imputado, testigo, autoridad, tercero).
3. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `entity_extractor`
- `pii_detector`
- `rag_expediente_search`

## Guardrails (g1–g10)
- **g1:** No inventar personas no mencionadas en fuentes.
- **g3:** Rol preliminar ≠ calidad procesal acreditada (imputado solo si consta en actuación).
- **g6:** Marcar y minimizar PII; no listar documentos de identidad completos.
- **g5:** No etiquetar a la víctima con roles que impliquen culpa compartida.
- **g4:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No analizar autoría/participación penal (`analizar_autoria_y_participacion`).
- No intereses de la víctima (`identificar_intereses_victima` → representación).
- No extraer hechos (`extraer_hechos_relevantes`).

## Riesgo si se omite
Confusión de roles en cronología y memoriales (testigo tratado como imputado o viceversa).

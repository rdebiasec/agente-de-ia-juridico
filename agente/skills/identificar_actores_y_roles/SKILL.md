<!-- config-version: 2; checksum: b2aba86a8d0f2232 -->
---
name: identificar-actores-y-roles
description: Contrato penal-víctimas: Extraer personas y entidades mencionadas en las fuentes y asignar rol procesal preliminar. Activar cuando el plan/HITL o el especialista requiera `identificar_actores_y_roles`. No sustituye a `analizar_autoria_y_participacion`.
disable-model-invocation: true
---

# identificar_actores_y_roles

## Scope
- Category: `Skills de hechos y cronologia`
- Skill ID: `identificar_actores_y_roles`
- Tier: `operativo`

## Used By Agents
- `analista_cronologia_hechos`
- `analista_representacion_victimas`

## Purpose
Extraer personas y entidades mencionadas en las fuentes y asignar rol procesal preliminar.

## Rol en analista_cronologia_hechos
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
Skills = contratos (no function_tools invocables). No existe tool LLM `identificar_actores_y_roles`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `entity_extractor` — no implementada
- `pii_detector` — no implementada
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar personas no mencionadas en fuentes.
- **Separar hecho de inferencia:** Rol preliminar ≠ calidad procesal acreditada (imputado solo si consta en actuación).
- **Confidencialidad:** Marcar y minimizar PII; no listar documentos de identidad completos.
- **No revictimizar:** No etiquetar a la víctima con roles que impliquen culpa compartida.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No analizar autoría/participación penal (`analizar_autoria_y_participacion`).
- No intereses de la víctima (`identificar_intereses_victima` → representación).
- No extraer hechos (`extraer_hechos_relevantes`).

## Riesgo si se omite
Confusión de roles en cronología y memoriales (testigo tratado como imputado o viceversa).

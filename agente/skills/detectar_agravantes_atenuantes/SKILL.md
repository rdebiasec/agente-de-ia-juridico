<!-- config-version: 4; checksum: cf47d03b5342ec2c -->
---
name: detectar-agravantes-atenuantes
description: Contrato penal-víctimas: Identificar circunstancias de agravación o atenuación aplicables con soporte factual y normativo preliminar. Activar cuando el plan/HITL o el especialista requiera `detectar_agravantes_atenuantes`. No sustituye a `descomponer_elementos_tipo_penal`.
disable-model-invocation: true
---

# detectar_agravantes_atenuantes

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `detectar_agravantes_atenuantes`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad`

## Purpose
Identificar circunstancias de agravación o atenuación aplicables con soporte factual y normativo preliminar.

## Rol en analista_responsabilidad_tipicidad
Ejecutar tras descomposición del tipo y autoría. Relevante para gravedad de solicitudes de la víctima y expectativas de pena (sin prometer resultado).

## Fuentes KB
- `agente/conocimiento/penal.md` — marco tipico preliminar (no imputación).
- `agente/conocimiento/normas-clave.md` — criterio operativo y regla de citación.
- Herramientas: `leer_area_derecho(penal)`, `leer_normas_clave`, `buscar_en_conocimiento` antes de citar CP.
## Inputs
- Tipo penal hipotético y hechos soportados.
- Circunstancias del hecho (vínculo con víctima, premeditación, grupo, etc.).
- Norma penal verificada en RAG.

## Outputs
- Registro: `circunstancia`, `tipo` (agravante | atenuante | cualificadora), `norma_cp`, `hecho_soporte`, `prueba`, `estado` (acreditado | pendiente).
- Circunstancias no acreditadas marcadas `[PENDIENTE DE VERIFICAR]`.

## Steps
0. Antes de citar normas o cerrar hipótesis: leer Fuentes KB (`penal.md` / `normas-clave.md`) vía tools de grounding; sin soporte → `[PENDIENTE DE VERIFICAR]`.
1. Listar circunstancias narradas que *podrían* agravar/atenuar con ancla fáctica.
2. No sembrar artículos del CP sin Fuentes KB verificadas.
3. Separar hecho vs inferencia; marcar pendientes.
4. Entregar lista preliminar para revisión humana.


## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_agravantes_atenuantes`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_codigo_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inventar circunstancias ni artículos.
- **Separar hecho de inferencia:** Circunstancia alegada sin hecho = pendiente, no acreditada.
- **Revision humana obligatoria:** No prometer pena o resultado al cliente.
- **No revictimizar:** No usar circunstancias que culpen a la víctima (ej. “provocación” sin soporte).
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No descomponer tipo base (`descomponer_elementos_tipo_penal`).
- No enfoque diferencial (`analizar_enfoque_diferencial` → representación víctimas).

## Riesgo si se omite
Omisión de cualificadoras o agravantes que la Fiscalía sí podría argumentar, o alegación de agravante sin soporte.

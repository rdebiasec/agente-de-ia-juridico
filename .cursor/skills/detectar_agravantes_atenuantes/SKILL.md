<!-- config-version: 2; checksum: a7210394ff5cd215 -->
---
name: detectar-agravantes-atenuantes
description: Skill operativo penal-victimas: identificar circunstancias relevantes que puedan afectar gravedad juridica. Use when the workflow requires `detectar_agravantes_atenuantes`.
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

## Rol en analista_tipicidad
Ejecutar tras descomposición del tipo y autoría. Relevante para gravedad de solicitudes de la víctima y expectativas de pena (sin prometer resultado).

## Inputs
- Tipo penal hipotético y hechos soportados.
- Circunstancias del hecho (vínculo con víctima, premeditación, grupo, etc.).
- Norma penal verificada en RAG.

## Outputs
- Registro: `circunstancia`, `tipo` (agravante | atenuante | cualificadora), `norma_cp`, `hecho_soporte`, `prueba`, `estado` (acreditado | pendiente).
- Circunstancias no acreditadas marcadas `[PENDIENTE DE VERIFICAR]`.

## Steps
1. Revisar hechos que configuren agravantes o atenuantes aplicables.
2. Vincular con norma penal y prueba disponible.
3. Marcar elementos no acreditados como pendientes.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

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

## Guardrails (g1–g10)
- **g1:** No inventar circunstancias ni artículos.
- **g3:** Circunstancia alegada sin hecho = pendiente, no acreditada.
- **g4:** No prometer pena o resultado al cliente.
- **g5:** No usar circunstancias que culpen a la víctima (ej. “provocación” sin soporte).
- **g8:** Aviso de revisión profesional.

## No duplicar
- No descomponer tipo base (`descomponer_elementos_tipo_penal`).
- No enfoque diferencial (`analizar_enfoque_diferencial` → representación víctimas).

## Riesgo si se omite
Omisión de cualificadoras o agravantes que la Fiscalía sí podría argumentar, o alegación de agravante sin soporte.

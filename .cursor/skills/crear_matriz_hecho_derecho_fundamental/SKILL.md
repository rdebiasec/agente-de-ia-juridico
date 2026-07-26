---
name: crear-matriz-hecho-derecho-fundamental
description: Skill estrategico penal-victimas: relacionar hechos con derechos afectados. Use when the workflow requires `crear_matriz_hecho_derecho_fundamental`.
disable-model-invocation: true
---

# crear_matriz_hecho_derecho_fundamental

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `crear_matriz_hecho_derecho_fundamental`
- Tier: `estrategico`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`

## Purpose
Vincular cada hecho relevante con el derecho fundamental comprometido y la conducta omisiva o activa de la autoridad.

## Rol en evaluador_derechos_fundamentales_tutela
Base factual-constitucional para `evaluar_procedencia_tutela` y `preparar_borrador_tutela_preliminar`.

## Inputs
- Hechos verificados y narrados (`verificar_hechos_soportados`, cronología).
- Derechos identificados (`identificar_derecho_fundamental_afectado`, si existe).
- Autoridades y actuaciones u omisiones imputadas.

## Outputs
- Matriz: `hecho` | `fuente` | `derecho_fundamental` | `conducta_omisiva_activa` | `soporte` (confirmado | narrado | pendiente).
- Vacíos probatorios por derecho invocado.
- Norma constitucional de soporte preliminar (verificada en RAG).
- Etiqueta: `MATRIZ CONSTITUCIONAL PRELIMINAR`.

## Steps
1. Listar hechos verificables y narrados relevantes para la vulneración alegada.
2. Relacionar cada hecho con el derecho fundamental comprometido y la conducta omisiva/activa.
3. Señalar vacíos probatorios y norma constitucional de soporte preliminar.
4. Ordenar filas por relevancia para pretensiones de tutela.
5. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `crear_matriz_hecho_derecho_fundamental`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_constitucion_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails (g1–g10)
- **g1:** No inventar hechos ni artículos constitucionales.
- **g3:** Hecho sin fuente → `[PENDIENTE DE VERIFICAR]`; no inferir vulneración.
- **g4:** HITL obligatorio; matriz preliminar — no sustituye `evaluar_procedencia_tutela`.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No identificar derechos en abstracto (`identificar_derecho_fundamental_afectado`).
- No matriz penal hecho-prueba (`construir_matriz_hecho_prueba`).

## Riesgo si se omite
Tutela con pretensiones desconectadas de hechos probados o derechos mal invocados.

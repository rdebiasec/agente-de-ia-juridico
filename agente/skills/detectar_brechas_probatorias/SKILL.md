<!-- config-version: 3; checksum: 07bae43d7367ac0e -->
---
name: detectar-brechas-probatorias
description: Contrato penal-víctimas: Identificar hechos relevantes sin prueba suficiente en el expediente. Activar cuando el plan/HITL o el especialista requiera `detectar_brechas_probatorias`. No sustituye a `crear_plan_recaudo_probatorio`.
disable-model-invocation: true
---

# detectar_brechas_probatorias

## Scope
- Category: `Skills de evidencia y soporte probatorio`
- Skill ID: `detectar_brechas_probatorias`
- Tier: `operativo`

## Used By Agents
- `analista_evidencia`
- `analista_representacion_victimas`

## Purpose
Identificar hechos relevantes sin prueba suficiente en el expediente.

## Rol en analista_evidencia
Antecede plan de recaudo.

## Rol en analista_representacion_victimas
Informa debilidades para teoría del caso.

## Fuentes KB
- Matriz hecho-prueba / inventario del expediente; no asumir prueba no inventariada.
- `agente/conocimiento/proceso-penal-906.md` — impacto de la brecha según etapa (descubrimiento/juicio) si consta.
- `agente/conocimiento/normas-clave.md` — priorizar pretensión de la víctima sin culpar por “falta de prueba”.
- Tools reales: `buscar_en_expediente`, `buscar_en_conocimiento`.

## Inputs
- Matriz hecho-prueba (`construir_matriz_hecho_prueba`).
- Inventario de evidencia (`inventariar_evidencia`).

## Outputs
- `brechas`: hecho | prueba_ausente_o_débil | impacto (alto | medio | bajo).
- `prioridad_recaudo` ordenada.
- Etiqueta: `BRECHAS PROBATORIAS PRELIMINARES`.

## Steps
1. Partir del inventario/matriz disponible.
2. Listar hechos esenciales sin medio de prueba suficiente.
3. Priorizar brechas por impacto en pretensión de la víctima.
4. No inventariar de nuevo ni redactar memorial.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_brechas_probatorias`.

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
- **No inventar:** No asumir prueba existente sin constar en inventario.
- **Oportunidad y terminos Ley 906:** Sin plazo, notificación o etapa Ley 906 verificados, no certificar oportunidad; marcar `[PENDIENTE DE VERIFICAR]`.
- **Revision humana obligatoria:** HITL obligatorio antes de usar la salida en memorial, estrategia o comunicación con cliente.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No plan de recaudo (`crear_plan_recaudo_probatorio`).
- No suficiencia global (`evaluar_suficiencia_probatoria`).

## Riesgo si se omite
Estrategia o memorial que depende de prueba que no existe ni está en camino.

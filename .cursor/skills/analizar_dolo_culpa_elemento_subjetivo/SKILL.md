<!-- config-version: 3; checksum: 8ee4009aea53dd56 -->
---
name: analizar-dolo-culpa-elemento-subjetivo
description: Contrato penal-víctimas: Identificar indicios factuales que podrían soportar dolo, culpa u otro elemento subjetivo, sin afirmar certeza. Activar cuando el plan/HITL o el especialista requiera `analizar_dolo_culpa_elemento_subjetivo`. No sustituye a `descomponer_elementos_tipo_...
disable-model-invocation: true
---

# analizar_dolo_culpa_elemento_subjetivo

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_dolo_culpa_elemento_subjetivo`
- Tier: `operativo`

## Used By Agents
- `analista_responsabilidad_tipicidad`

## Purpose
Identificar indicios factuales que podrían soportar dolo, culpa u otro elemento subjetivo, sin afirmar certeza.

## Rol en analista_responsabilidad_tipicidad
Ejecutar tras descomposición de elementos cuando el tipo exige dolo o culpa. Crítico en delitos que admiten modalidad culposa vs dolosa.

## Inputs
- Elementos subjetivos del tipo penal descompuesto.
- Hechos sobre intención, conocimiento, advertencia, inobservancia de deber.
- Declaraciones y conductas posteriores al hecho (si constan).

## Outputs
- `modalidad_preliminar`: dolo_directo | dolo_eventual | culpa_consciente | culpa_inconsciente | indeterminado.
- `hechos_soporte` e `indicios` (separados).
- `debilidades` y prueba pendiente.
- Etiqueta: `NO AFIRMAR ELEMENTO SUBJETIVO SIN SOPORTE`.

## Steps
1. Partir del elemento subjetivo exigido por el tipo ya descompuesto (`penal.md` §Elemento subjetivo).
2. Checklist de indicios (separar hecho vs indicio): conocimiento; voluntad/aceptación del resultado; inobservancia del deber de cuidado.
3. Asignar `modalidad_preliminar` (dolo_directo | dolo_eventual | culpa_consciente | culpa_inconsciente | indeterminado) solo con soporte; si solo hay resultado → indeterminado.
4. Listar debilidades y prueba pendiente; etiqueta `NO AFIRMAR ELEMENTO SUBJETIVO SIN SOPORTE`.
5. Marcar `[PENDIENTE DE VERIFICAR]` y someter a revisión humana antes de memorial.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `analizar_dolo_culpa_elemento_subjetivo`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `rag_expediente_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto
- `rag_jurisprudencia_penal_search` — usar `buscar_en_conocimiento` / `buscar_en_expediente` mientras tanto

## Guardrails
- **No inventar:** No inferir dolo solo del resultado; exigir hechos de conocimiento/voluntad.
- **Separar hecho de inferencia:** Indicio ≠ prueba de dolo; etiquetar separadamente.
- **Revision humana obligatoria:** Conclusión subjetiva nunca va a memorial sin abogado.
- **No revictimizar:** En violencia sexual, no inferir consentimiento o dolo de la víctima.
- **Aviso de borrador:** Aviso de revisión profesional.


## Fuentes KB (obligatorio consultar antes de citar norma)
- `agente/conocimiento/penal.md` — marco tipico, dolo/culpa, autoría, agravantes.
- `agente/conocimiento/normas-clave.md` — marco Ley 599/906 + checklist de citación.
- Tools: `leer_area_derecho` (penal), `leer_normas_clave`, `buscar_en_conocimiento`.
- Artículo concreto no verificado → `[PENDIENTE DE VERIFICAR]`. No inventar normas.

## No duplicar
- No descomponer tipo (`descomponer_elementos_tipo_penal`).
- No jurisprudencia de fondo (`verificar_jurisprudencia` → `analista_calidad_juridica`).
- No preguntas a víctima (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Calificación por delito doloso cuando los hechos solo soportan culpa (o viceversa), o archivo por atipicidad subjetiva.

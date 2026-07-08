---
name: analizar-dolo-culpa-elemento-subjetivo
description: Skill operativo penal-victimas: identificar hechos que podrian soportar dolo, culpa u otro elemento subjetivo. Use when the workflow requires `analizar_dolo_culpa_elemento_subjetivo`.
disable-model-invocation: true
---

# analizar_dolo_culpa_elemento_subjetivo

## Scope
- Category: `Skills de tipicidad y responsabilidad penal`
- Skill ID: `analizar_dolo_culpa_elemento_subjetivo`
- Tier: `operativo`

## Used By Agents
- `analista_tipicidad_y_responsabilidad_penal`

## Purpose
Identificar indicios factuales que podrían soportar dolo, culpa u otro elemento subjetivo, sin afirmar certeza.

## Rol en analista_tipicidad
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
1. Analizar elementos subjetivos (dolo, culpa) según hechos narrados.
2. Distinguir intención, conocimiento y negligencia preliminarmente.
3. No afirmar elemento subjetivo sin soporte suficiente.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_expediente_search`
- `rag_jurisprudencia_penal_search`

## Guardrails (g1–g10)
- **g1:** No inferir dolo solo del resultado; exigir hechos de conocimiento/voluntad.
- **g3:** Indicio ≠ prueba de dolo; etiquetar separadamente.
- **g4:** Conclusión subjetiva nunca va a memorial sin abogado.
- **g5:** En violencia sexual, no inferir consentimiento o dolo de la víctima.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No descomponer tipo (`descomponer_elementos_tipo_penal`).
- No jurisprudencia de fondo (`verificar_jurisprudencia` → calidad).
- No preguntas a víctima (`generar_preguntas_tipicidad`).

## Riesgo si se omite
Calificación por delito doloso cuando los hechos solo soportan culpa (o viceversa), o archivo por atipicidad subjetiva.

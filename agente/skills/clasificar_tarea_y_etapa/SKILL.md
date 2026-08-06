<!-- config-version: 3; checksum: 1d785e286072cef0 -->
---
name: clasificar-tarea-y-etapa
description: Contrato penal-víctimas: Entender qué pide el despacho en el turno, clasificar el tipo de tarea y ubicar la etapa procesal aparente para derivar al especialista correcto o pedir datos faltantes. Activar cuando el plan/HITL o el especialista requiera `clasificar_tarea_y_etapa`....
disable-model-invocation: true
---

# clasificar_tarea_y_etapa

## Scope
- Category: `Skills transversales`
- Skill ID: `clasificar_tarea_y_etapa`
- Tier: `operativo`

## Index Blurb
Triage del turno: tipo de tarea + etapa aparente + agente destino o faltantes.

## Used By Agents
- `coordinador_caso` (skill primario del agente)
- `analista_ruta_procesal`

## Purpose
Entender qué pide el despacho en el turno, clasificar el tipo de tarea y ubicar la etapa procesal aparente para derivar al especialista correcto o pedir datos faltantes.

## Rol en coordinador_caso
Primer skill en cada consulta nueva. En runtime el contrato lo materializa `build_triage` (`src/agents/triage.py` → `TriageResult`); el LLM no re-clasifica si ya hay `[TRIAGE_SISTEMA]`.

## Inputs
- Solicitud textual del abogado o usuario interno.
- Resumen de caso y radicado (si existe).
- Documentos disponibles en el turno o expediente.
- Estado procesal conocido (última actuación, audiencia programada, etapa declarada).

## Outputs
Alineados a `TriageResult` (`src/agents/schemas.py`):
- `tipo_tarea`: `redaccion` | `analisis_factual` | `tipicidad` | `ruta_906` | `representacion_victima` | `evidencia` | `audiencia` | `seguimiento` | `fuera_de_alcance`.
- `etapa_aparente`: `indagacion` | `investigacion` | `imputacion` | `juicio` | `ejecucion` | `desconocida` | `pendiente_verificar`.
- `agente_destino` recomendado (agent id).
- `datos_faltantes_bloqueantes` (lista corta de labels) o confirmación de derivación.
- `puede_continuar`: bool.
- `urgencia_preliminar`: bool (true si `nivel_urgencia` ∈ {critica, alta}).
- `nivel_urgencia`: `critica` | `alta` | `media` | `baja`.
- `motivos_urgencia`, `escalar_humano`, `accion_inmediata_urgencia`.

## Steps
1. Clasificar tipo de tarea y etapa aparente con base en el mensaje.
2. Alinear con triage de sistema; no contradecir `[TRIAGE_SISTEMA]`.
3. No hacer análisis de fondo de tipicidad/cronología.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `clasificar_tarea_y_etapa`.

### Function tools (LLM, si aplica en el turno)
- `buscar_en_expediente` (sesión activa vinculada)

### Side-effects de código (no son function_tools)
- `gerencia_ledger` — triage/completitud en `src/agents/triage.py` + `src/agents/completeness.py`
- `audit_trace` — spans del runner / pipeline

## Guardrails
- **No inventar:** No inventar etapa, radicado ni actuaciones para justificar derivación.
- **Pedir datos faltantes:** Sin radicado ni actuaciones mínimas, no concluir etapa; marcar `desconocida` y pedir datos.
- **Separar hecho de inferencia:** Etapa aparente es hipótesis de enrutamiento, no conclusión procesal definitiva.
- **Revision humana obligatoria:** Derivación con implicación estratégica (memorial, audiencia, impulso) requiere revisión del abogado.
- **Fuera de alcance:** Consultas no penales o ajenas a representación de víctimas en Colombia → declarar fuera de alcance y no derivar a redactor.
- **Aviso de borrador:** Cerrar con aviso de revisión profesional.

## Handoff
- Análisis factual → `analista_cronologia_hechos` (`extraer_hechos_relevantes`).
- Tipicidad / calificación → `analista_responsabilidad_tipicidad` (solo con hechos mínimos).
- Ruta Ley 906 → `analista_ruta_procesal`.
- Urgencia detectada → contrato `detectar_urgencia_penal` / `assess_urgency` antes de derivar.

## No duplicar
- No determinar etapa con rigor procesal (`identificar_etapa_procesal_ley906` → especialista ruta 906).
- No inventariar faltantes documentales (`gestionar_faltantes_expediente`).
- No evaluar urgencia en detalle (`detectar_urgencia_penal`).

## Best Practices
- Preferir `etapa_aparente=desconocida` + pregunta concreta antes que inventar etapa.
- Una sola `agente_destino` primaria; secuencia solo si el turno lo exige explícitamente.
- Si `urgencia_preliminar=true`, no saltar a redacción.

## Riesgo si se omite
Derivación errónea retrasa actuaciones, mezcla competencias y puede hacer perder términos en Ley 906.

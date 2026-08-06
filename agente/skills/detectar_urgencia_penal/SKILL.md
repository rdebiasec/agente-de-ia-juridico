<!-- config-version: 3; checksum: 86ff4383c4a2d193 -->
---
name: detectar-urgencia-penal
description: Contrato penal-víctimas: Detectar si el caso o el turno exigen atención humana inmediata por riesgo a derechos, términos, integridad o pérdida probatoria. Activar cuando el plan/HITL o el especialista requiera `detectar_urgencia_penal`. No sustituye a `generar_alertas_terminos...
disable-model-invocation: true
---

# detectar_urgencia_penal

## Scope
- Category: `Skills transversales`
- Skill ID: `detectar_urgencia_penal`
- Tier: `estrategico`

## Index Blurb
Clasifica urgencia (critica/alta/media/baja) y si hay que escalar al humano antes del fondo.

## Used By Agents
- `coordinador_caso`
- `analista_seguimiento_procesal`
- `analista_calidad_juridica`

## Purpose
Detectar si el caso o el turno exigen atención humana inmediata por riesgo a derechos, términos, integridad o pérdida probatoria.

## Rol en coordinador_caso
Contrato materializado por `assess_urgency` (`src/agents/urgency.py` → `UrgencyResult`) e integrado en `build_triage` / `[TRIAGE_SISTEMA]`. El LLM no re-clasifica el nivel.

## Inputs
- Solicitud del turno y hechos reportados.
- Fechas de audiencias, términos o vencimientos mencionados o en expediente.
- Indicios de riesgo a integridad de la víctima, libertad, destrucción de evidencia o silencio procesal prolongado.
- Estado del radicado y última actuación (si existe).

## Outputs
Alineados a `UrgencyResult` / campos de `TriageResult`:
- `nivel_urgencia`: `critica` | `alta` | `media` | `baja`.
- `motivos` (lista verificable o `[PENDIENTE DE VERIFICAR]`).
- `accion_inmediata_sugerida` (ej. contactar abogado titular, preservar evidencia, verificar término).
- `escalar_humano`: bool (true si critica|alta).
- `urgencia_preliminar`: bool derivado (`critica`|`alta` → true).
- `evaluada_en`: unix timestamp.

## Steps
1. Evaluar indicios de urgencia (riesgo, términos, violencia, menor).
2. Asignar nivel y si escala a humano; no bajar urgencia de sistema.
3. No sustituir análisis de fondo.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `detectar_urgencia_*`.

### Function tools (LLM, si aplica en el turno)
- `buscar_en_expediente` (sesión activa vinculada; contexto, no reclasifica)

### Side-effects de código (no son function_tools)
- `assess_urgency` — `src/agents/urgency.py` (niveles critica|alta|media|baja)
- `gerencia_ledger` — `metricas_gerencia["ultima_urgencia"]` vía `persist_verification`
- `audit_trace` — span de escalamiento en runner cuando critica/alta (no trivial)

## Guardrails
- **No inventar:** No inventar vencimientos ni amenazas no reportadas.
- **Pedir datos faltantes:** Si falta fecha de audiencia o término crítico, marcar urgencia `[PENDIENTE DE VERIFICAR]` y pedir dato.
- **Separar hecho de inferencia:** Distinguir riesgo reportado de inferencia de la IA.
- **Revision humana obligatoria:** Nivel critica/alta siempre requiere confirmación humana antes de actuar.
- **No revictimizar:** En riesgo a integridad, no exponer datos sensibles de la víctima en la notificación de escalamiento.
- **Aviso de borrador:** Aviso de que la urgencia es preliminar y debe confirmar el abogado.

## Handoff
- critica/alta → notificación humana +, si aplica, `analista_seguimiento_procesal` o especialista según motivo.
- media/baja → continuar triage (`clasificar_tarea_y_etapa` / faltantes).

## No duplicar
- No calcular todos los términos del caso (`generar_alertas_terminos_vencimientos`).
- No preservar evidencia digital (`preservar_evidencia_digital`).

## Best Practices
- Ante duda entre media y alta, preferir alta y pedir confirmación humana.
- No incluir datos sensibles de la víctima en el texto de escalamiento.

## Riesgo si se omite
Pérdida de términos, deterioro probatorio o falta de protección oportuna a la víctima.

---
name: recomendar-via-constitucional-o-alternativa
description: Skill operativo penal-victimas: recomendar tutela, derecho de peticion, solicitud procesal, queja u otra ruta. Use when the workflow requires `recomendar_via_constitucional_o_alternativa`.
disable-model-invocation: true
---

# recomendar_via_constitucional_o_alternativa

## Scope
- Category: `Skills constitucionales y tutela`
- Skill ID: `recomendar_via_constitucional_o_alternativa`
- Tier: `operativo`

## Used By Agents
- `evaluador_derechos_fundamentales_tutela`
- `coordinador_expediente_penal`

## Purpose
Inventariar vías disponibles (tutela, petición, solicitud Ley 906, queja, etc.), compararlas preliminarmente y recomendar ruta preferente con riesgos.

## Rol en coordinador
**Solo triage constitucional-procesal:** orientar si conviene escalar a `evaluador_derechos_fundamentales_tutela` o usar vía ordinaria penal. **No** sustituye `evaluar_procedencia_tutela` ni autoriza redacción de tutela.

## Inputs
- Hechos que motivan la acción (verificados o `[PENDIENTE DE VERIFICAR]`).
- Etapa procesal penal y actuaciones ordinarias pendientes o agotadas.
- Derecho fundamental o interés alegado (participación, información, reparación, protección).
- Peticiones o silencios de autoridad ya ocurridos (si constan).

## Outputs
- Inventario de vías: `tutela` | `derecho_peticion` | `solicitud_ley906` | `queja` | `otra` | `aguardar_ordinario`.
- Comparación preliminar: oportunidad, celeridad, riesgo de improcedencia.
- `via_preferente_preliminar` + justificación + riesgos.
- `siguiente_paso`: derivar a `evaluador_derechos_fundamentales_tutela` | `analista_ruta_procesal_ley906` | `redactor_documentos_juridicos_penales` (solo si vía ordinaria clara).
- Etiqueta obligatoria si se menciona tutela: `NO REDACTAR TUTELA SIN DICTAMEN DE PROCEDENCIA`.

## Steps
1. Inventariar vías disponibles: tutela, petición, solicitud Ley 906, queja, etc.
2. Comparar oportunidad, celeridad y probabilidad de éxito de cada vía.
3. Recomendar ruta preferente con justificación y riesgos.
4. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
- `rag_constitucional_search`
- `rag_ley906_search`

## Guardrails (g1–g10)
- **g1:** No citar sentencias de tutela ni artículos sin verificar en RAG.
- **g2:** Sin hechos mínimos y etapa, no recomendar tutela; pedir datos.
- **g3:** Subsidiariedad: señalar mecanismos ordinarios Ley 906 antes de tutela.
- **g4:** HITL obligatorio; coordinador **nunca** aprueba procedencia de tutela ni entrega borrador.
- **g5:** No sugerir exposición pública de la víctima como vía preferente sin valorar revictimización.
- **g7:** Solo contexto penal-víctimas Colombia.
- **g8:** Aviso de revisión profesional y de que tutela requiere evaluador constitucional.

## No duplicar
- No evaluar legitimación, subsidiariedad, inmediatez (`evaluar_procedencia_tutela`).
- No revisar mecanismos ordinarios en detalle (`revisar_mecanismos_ordinarios`).
- No redactar tutela (`redactar_tutela_penal_preliminar`).

## Riesgo si se omite
Tutela improcedente o prematura → rechazo, costos y debilitamiento de la vía ordinaria penal.

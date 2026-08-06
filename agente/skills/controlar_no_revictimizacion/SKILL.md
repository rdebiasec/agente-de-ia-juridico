<!-- config-version: 3; checksum: 8910b04454b85269 -->
---
name: controlar-no-revictimizacion
description: Contrato penal-víctimas: Detectar lenguaje, preguntas o estrategias que culpen, minimicen o expongan indebidamente a la víctima; proponer reformulaciones. Activar cuando el plan/HITL o el especialista requiera `controlar_no_revictimizacion`. No sustituye a `clasificar_aprobaci...
disable-model-invocation: true
---

# controlar_no_revictimizacion

## Scope
- Category: `Skills de calidad juridica`
- Skill ID: `controlar_no_revictimizacion`
- Tier: `critico`

## Used By Agents
- `analista_calidad_juridica`
- `analista_representacion_victimas`

## Purpose
Detectar lenguaje, preguntas o estrategias que culpen, minimicen o expongan indebidamente a la víctima; proponer reformulaciones.

## Rol en analista_calidad_juridica
Filtro obligatorio antes de aprobar escritos, preguntas de audiencia o comunicaciones al cliente.

## Rol en analista_representacion_victimas
Revisión temprana de teoría del caso y materiales dirigidos a la víctima.

## Inputs
- Texto a revisar (memorial, guion, preguntas, resumen cliente, teoría del caso).
- Tipo de audiencia o documento y destinatario (juez, víctima, Fiscalía).
- Contexto del delito (violencia sexual, intrafamiliar, etc.) si consta.

## Outputs
- `hallazgos`: lista con `fragmento`, `tipo_riesgo` (culpabilización | minimización | exposición_gráfica | dato_sensible_innecesario | pregunta_inductiva), `severidad` (alta | media | baja).
- `reformulaciones_sugeridas` por hallazgo.
- `riesgo_residual` y decisión recomendada: `ajustar` | `escalar_abogado` | `sin_hallazgos`.
- Etiqueta: `REVISIÓN REVICTIMIZACIÓN — NO ENVIAR SIN ABOGADO`.

## Steps
1. Revisar lenguaje que culpe, minimice o exponga indebidamente a la víctima.
2. Evaluar preguntas y estrategias propuestas con enfoque de derechos.
3. Detectar exposición innecesaria de datos sensibles o relato gráfico.
4. Proponer reformulaciones respetuosas y centradas en derechos.
5. Documentar riesgos residuales para decisión del abogado.
6. Entregar salida estructurada, marcar `[PENDIENTE DE VERIFICAR]` lo no soportado y someter a revisión humana.

## Tools
Skills = contratos (no function_tools invocables). No existe tool LLM `controlar_no_revictimizacion`.

### Function tools (LLM, si aplica)
- `buscar_en_expediente` (sesión activa vinculada)
- `buscar_en_conocimiento` (KB / normas)
- `leer_area_derecho` — lectura MD de área (plan/especialistas; chat Gerente slim off)
- `leer_playbook_proceso` — playbook Ley 906 (plan/especialistas)
- `leer_normas_clave` — normas penales clave (plan/especialistas)
- `listar_areas_derecho` — catálogo de áreas (plan/especialistas según necesidad; chat Gerente off)

### Planned capabilities (no implementadas — no invocar como tools)
- `revictimization_risk_checker` — no implementada

## Guardrails
- **No inventar:** No inventar conductas de la víctima ni contexto no documentado.
- **No revictimizar:** Prohibido sugerir que la víctima “provocó”, “consintió tácitamente” o “debió denunciar antes” sin prueba.
- **Confidencialidad:** No reproducir detalles gráficos innecesarios en reformulaciones.
- **Revision humana obligatoria:** HITL obligatorio; no aprobar salida con hallazgos de severidad alta.
- **Aviso de borrador:** Aviso de revisión profesional.

## No duplicar
- No clasificar aprobación final (`clasificar_aprobacion_juridica`).
- No detectar riesgo abstracto (`detectar_riesgo_revictimizacion` — alerta temprana).

## Riesgo si se omite
La víctima recibe preguntas humillantes, escritos que la culpan o exposición pública innecesaria del relato.

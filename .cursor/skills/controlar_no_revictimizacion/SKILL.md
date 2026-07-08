---
name: controlar-no-revictimizacion
description: Skill critico penal-victimas: revisar que la salida no culpe ni exponga indebidamente a la victima. Use when the workflow requires `controlar_no_revictimizacion`.
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
- `revictimization_risk_checker`

## Guardrails (g1–g10)
- **g1:** No inventar conductas de la víctima ni contexto no documentado.
- **g5:** Prohibido sugerir que la víctima “provocó”, “consintió tácitamente” o “debió denunciar antes” sin prueba.
- **g6:** No reproducir detalles gráficos innecesarios en reformulaciones.
- **g4:** HITL obligatorio; no aprobar salida con hallazgos de severidad alta.
- **g8:** Aviso de revisión profesional.

## No duplicar
- No clasificar aprobación final (`clasificar_aprobacion_juridica`).
- No detectar riesgo abstracto (`detectar_riesgo_revictimizacion` — alerta temprana).

## Riesgo si se omite
La víctima recibe preguntas humillantes, escritos que la culpan o exposición pública innecesaria del relato.

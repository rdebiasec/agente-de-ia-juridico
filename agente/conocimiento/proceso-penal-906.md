# Playbook procesal penal — Sistema acusatorio (Ley 906 de 2004)

**Última revisión:** 2026-08-05
**Uso:** guía de etapas del proceso penal de tendencia acusatoria. Confírmese siempre con la norma vigente; no afirmar artículos que no estén verificados.

## Etapas (canónicas para skills)

Usar estas etiquetas en `identificar_etapa_procesal_ley906` y rutas derivadas.
Aliases aceptados entre paréntesis.

1. **indagacion_investigacion** — Indagación e investigación. La Fiscalía adelanta la noticia criminal y los actos de investigación. *(alias: indagación, investigación)*
2. **audiencias_preliminares_garantias** — Audiencias preliminares ante juez de control de garantías (legalización de captura, control de actos que afectan derechos fundamentales).
3. **formulacion_imputacion** — Formulación de imputación ante juez de control de garantías.
4. **medida_aseguramiento** — Solicitud y decisión de medida de aseguramiento, cuando procede.
5. **acusacion** — Escrito de acusación y audiencia de formulación de acusación ante juez de conocimiento. *(alias: etapa_intermedia)*
6. **audiencia_preparatoria** — Descubrimiento probatorio, enunciación y admisión de pruebas.
7. **juicio_oral** — Práctica de pruebas, alegatos, sentido del fallo y sentencia. *(alias: juicio)*
8. **recursos** — Reposición, apelación y, cuando procede, casación.
9. **ejecucion_penal** — Fase de ejecución (si aplica al caso).
10. **archivo** — Archivo / preclusión / terminación (solo con actuación verificable).
11. **pendiente_verificar** — Insuficientes actuaciones o fechas → `[PENDIENTE DE VERIFICAR]`.

## Distinciones clave

- **Juez de control de garantías** (etapa preliminar) vs. **juez de conocimiento** (acusación, preparatoria y juicio).
- Salidas alternas: preacuerdos y negociaciones, principio de oportunidad (verificar procedencia).

## Rol del despacho

Actúa como **representante de víctima**. Confirmar siempre interés de la víctima, etapa procesal y objetivo antes de preparar audiencias, interrogatorios o memoriales.

## Términos

- Los términos y plazos procesales se cuentan en **días hábiles** (verificar regla aplicable al acto).
- Sin **fecha base** (notificación / actuación fundante) no se cierra fecha límite: marcar pendiente.
- Toda estimación de IA lleva etiqueta `ESTIMACIÓN IA — VERIFICAR CON ABOGADO`.
- El cálculo automático y alertas de calendario son apoyo; no sustituyen al abogado.

## Relación con skills de ruta

| Skill | Ancla en este playbook |
|---|---|
| `identificar_etapa_procesal_ley906` | §Etapas canónicas |
| `crear_ruta_procesal_recomendada` | secuencia según etapa + intereses víctima |
| `evaluar_oportunidad_procesal` / `controlar_terminos_procesales_preliminares` | §Términos |
| `detectar_riesgos_procesales` / `detectar_inactividad_procesal` | etapa + actuaciones + plazos |

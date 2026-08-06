# Playbook procesal penal — Sistema acusatorio (Ley 906 de 2004)

**Última revisión:** 2026-08-05
**Uso:** guía de etapas del proceso penal de tendencia acusatoria. Confírmese siempre con la norma vigente; no afirmar artículos que no estén verificados.

## Etapas

1. **Indagación e investigación.** La Fiscalía adelanta la noticia criminal y los actos de investigación.
2. **Audiencias preliminares ante juez de control de garantías.** Legalización de captura, control de actos que afectan derechos fundamentales.
3. **Formulación de imputación.** La Fiscalía comunica los cargos ante el juez de control de garantías.
4. **Medida de aseguramiento.** Cuando procede, se solicita y decide.
5. **Acusación.** Escrito de acusación y audiencia de formulación de acusación ante el juez de conocimiento.
6. **Audiencia preparatoria.** Descubrimiento probatorio, enunciación y admisión de pruebas.
7. **Juicio oral.** Práctica de pruebas, alegatos, sentido del fallo y sentencia.
8. **Recursos.** Reposición, apelación y, cuando procede, casación.

### Enum operativo (`etapa_ley906`) — alias canónicos

Para skills/schemas usar **un** valor de esta lista (mapear relatos libres aquí):

| Valor canónico | Playbook |
|---|---|
| `indagacion_investigacion` | Etapa 1 |
| `audiencias_preliminares` | Etapa 2 |
| `formulacion_imputacion` | Etapa 3 |
| `medida_aseguramiento` | Etapa 4 |
| `acusacion` | Etapa 5 |
| `audiencia_preparatoria` | Etapa 6 |
| `juicio_oral` | Etapa 7 |
| `recursos` | Etapa 8 |
| `ejecucion_penal` | Post-sentencia / ejecución (si consta) |
| `archivo` | Archivo o preclusión acreditada |
| `pendiente_verificar` | Sin actuación fundante |

Aliases tolerados al mapear: `indagación`/`investigación` → `indagacion_investigacion`; `etapa_intermedia` → suele cubrir imputación/acusación/preparatoria (desambiguar con actuación); `juicio` → `juicio_oral`.

## Distinciones clave

- **Juez de control de garantías** (etapa preliminar) vs. **juez de conocimiento** (acusación, preparatoria y juicio).
- Salidas alternas: preacuerdos y negociaciones, principio de oportunidad (verificar procedencia).

## Rol del despacho

Actúa como **representante de víctima**. Confirmar siempre interés de la víctima, etapa procesal y objetivo antes de preparar audiencias, interrogatorios o memoriales.

## Términos

- Los términos y plazos procesales se cuentan en **días hábiles** (Ley 906), salvo norma especial verificada.
- Sin `fecha_base` (notificación/actuación fundante) **no** certificar vencimiento ni extemporaneidad.
- Toda estimación de plazo lleva etiqueta `ESTIMACIÓN IA — VERIFICAR CON ABOGADO` y, si falta soporte, `[PENDIENTE DE VERIFICAR]`.
- El cálculo automático de calendario y alertas operativas puede estar parcial; la verificación humana es obligatoria antes de radicar.

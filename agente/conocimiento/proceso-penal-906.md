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

## Checklist evidencia / prueba (ancla skills O4)

Uso operativo para `analista_evidencia` (sin inventar artículos ni admisibilidad):

1. Inventariar medios allegados o narrados; separar existente vs solo narrado.
2. Clasificar tipología preliminar (documental, testimonial, pericial, digital, física, institucional).
3. Matriz hecho ↔ prueba; marcar soporte directo / indiciario / ausente / pendiente.
4. Detectar brechas críticas para la pretensión de la víctima; priorizar recaudo.
5. Integridad: no alterar digitales; alertar cadena de custodia dudosa → escalar humano/perito.
6. Cruzar etapa aparente (`etapa_ley906`): descubrimiento/admisión suele concentrarse en **audiencia preparatoria** y práctica en **juicio oral**; sin actuación fundante → `pendiente_verificar`.
7. Plan de recaudo = borrador interno; oficios/contactos/pericias pasan por HITL abogado.
8. Sin `fecha_base` no certificar plazos de aporte o descubrimiento.

## Rol del despacho

Actúa como **representante de víctima**. Confirmar siempre interés de la víctima, etapa procesal y objetivo antes de preparar audiencias, interrogatorios o memoriales.

## Checklist intervención / representación de la víctima (ancla O5)

Sin inventar facultades ni artículos del CPP:

1. Confirmar intereses de la víctima y etapa `etapa_ley906` (o `pendiente_verificar`).
2. Mapear derechos aplicables (información, participación, protección, reparación) al momento procesal.
3. Listar actuaciones posibles de la representación en esa etapa; marcar improcedentes.
4. Evaluar riesgo de revictimización antes de proponer comparecencia, preguntas o exposición del relato.
5. Enfoque diferencial si constan factores de especial protección.
6. Teoría del caso y objetivos = borrador interno; no radicar ni comunicar al cliente sin abogado.
7. Intervención oral/táctica detallada → `analista_audiencias`; memorial → redactor + HITL.

## Checklist preparación de audiencias (ancla skills O6)

Uso operativo para `analista_audiencias` (sin inventar artículos ni fechas):

1. Confirmar tipo de audiencia, juez (garantías vs conocimiento) y `etapa_ley906` (o `pendiente_verificar`).
2. Definir objetivo jurídico y táctico de la víctima; alinear con teoría/intereses (insumo víctimas/ruta).
3. Marco de intervención procedente (`analizar_intervencion_victima`) antes de guion/preguntas/solicitudes.
4. Preparar guion breve, solicitudes orales y preguntas; separar hecho soportado de hipótesis táctica.
5. Anticipar riesgos (revictimización, revelación de estrategia, improvisación) y contraargumentos.
6. Checklist previo: documentos, poder, prueba a llevar, tiempos; no inventar fecha/hora/enlace.
7. Producto = preparación interna; **HITL obligatorio** antes de estrados — no sustituye oralidad del abogado.
8. Sin notificación/actuación fundante → no certificar oportunidad ni términos; marcar `[PENDIENTE DE VERIFICAR]`.

## Checklist redacción de piezas penales (ancla skills O7)

Uso operativo para `redactor_documentos_juridicos` (sin inventar artículos ni radicados):

1. Identificar tipo de pieza (memorial, impulso, petición, ampliación) y destinatario procesal.
2. Confirmar `etapa_ley906` (o `pendiente_verificar`); sin actuación fundante no afirmar oportunidad.
3. Estructurar **hechos → fundamentos → peticiones**; separar hecho confirmado/narrado/inferido.
4. Anclar hechos al expediente y normas a KB; sin soporte → `[PENDIENTE DE VERIFICAR]` (no inventar radicados, arts CPP ni anexos).
5. Derecho de petición: evaluar procedencia antes de redactar; no inventar plazos de respuesta.
6. Tono formal, respetuoso con la víctima; no revictimizar ni sobreprometer resultados.
7. Producto = **borrador interno**; etiqueta `BORRADOR — NO RADICAR SIN FIRMA`; **HITL obligatorio** (HIGH RISK) antes de uso externo.
8. Pasar a calidad jurídica cuando el plan lo indique; el abogado firma y radica.

## Checklist control de calidad jurídica (ancla skills O7 calidad/citas)

Uso operativo para `analista_calidad_juridica` (sin inventar normas, sentencias ni radicados):

1. Leer el borrador/análisis y listar citas (normas, jurisprudencia, radicados) y afirmaciones factuales.
2. Cruzar con expediente/KB (`buscar_en_expediente` / `buscar_en_conocimiento` / lecturas KB); sin soporte → `[PENDIENTE DE VERIFICAR]` o estado `no_localizada`/`pendiente`.
3. Cadena: coherencia estratégica → alucinaciones/citas/jurisprudencia → hechos soportados → confidencialidad / no revictimización → dictamen (`clasificar_aprobacion_juridica`).
4. Veredicto `DictamenCalidad`: `aprobable` | `con_cambios` | `rechazado` | `escalar`. Nunca aprobar en silencio.
5. `rechazado` / `escalar` = **gate duro**: no entrega accionable del plan hasta abogado.
6. No reescribir el memorial completo: hallazgos y cambios concretos; registrar `fuentes_kb` si se consultó KB/expediente.
7. Dictamen = preliminar de la IA; el abogado decide uso externo.

## Checklist seguimiento procesal operativo (ancla skills O8 parcial)

Uso operativo para `analista_seguimiento_procesal` (sin inventar radicados ni actuaciones):

1. Ubicar radicado y última actuación con fuente/timestamp (`monitorear_radicado` / `registrar_actuacion_procesal`); sin dato → `[PENDIENTE DE VERIFICAR]` (no simular portales externos).
2. Cruzar documentos radicados/enviados y respuestas (`seguimiento_documentos_radicados`).
3. Detectar inactividad material vs última actuación (`detectar_inactividad_procesal`); no inventar causas de la demora.
4. Alertas de términos/vencimientos (`generar_alertas_terminos_vencimientos`): días hábiles; sin `fecha_base` no certificar.
5. Consolidar reporte interno (`crear_reporte_estado_caso`); comunicación a cliente → HITL + `preparar_resumen_operativo_cliente` si aplica.
6. Impulso escrito o petición → escalar a `redactor_documentos_juridicos` vía Gerente (este agente no redacta piezas).
7. Registrar `fuentes_kb` si se consultó KB/expediente; salida accionable → HITL.

## Términos

- Los términos y plazos procesales se cuentan en **días hábiles** (Ley 906), salvo norma especial verificada.
- Sin `fecha_base` (notificación/actuación fundante) **no** certificar vencimiento ni extemporaneidad.
- Toda estimación de plazo lleva etiqueta `ESTIMACIÓN IA — VERIFICAR CON ABOGADO` y, si falta soporte, `[PENDIENTE DE VERIFICAR]`.
- El cálculo automático de calendario y alertas operativas puede estar parcial; la verificación humana es obligatoria antes de radicar.

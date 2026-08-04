# Guión docente — caso Laura R. (multiagente)

Manual de clase para abogados: cómo usar la firma virtual Lexiatek en un caso de **violencia intrafamiliar** y representación de víctima, con **Coordinador del Caso** + equipo interno, HITL y canal `/cliente`.

Anexo de hechos: [`hechos_caso_laura_vif.md`](./hechos_caso_laura_vif.md).

---

## 1. Antes de empezar

### URLs locales

| Pantalla | URL |
|----------|-----|
| Escritorio del abogado | http://127.0.0.1:8000/abogado |
| Portal de la víctima | http://127.0.0.1:8000/cliente |

Servidor: `./scripts/start-local.sh` (o el flujo local del proyecto).

### Qué pantallas mirar

| Zona | Para qué |
|------|----------|
| Chat central | Usted habla **solo** con el Coordinador del Caso |
| Expediente / bitácora | Hechos, radicado, hitos |
| **Equipo interno** | Pedidos del Gerente a especialistas (solo lectura) |
| **Borrador / Bandeja** | Piezas accionables y respuestas al cliente (aprobar / editar / rechazar) |
| Actividad | Trazas técnicas (opcional en clase) |

### Reglas de oro

1. La IA **propone**; usted **revisa y aprueba**.
2. La víctima en `/cliente` solo ve la voz del **Gerente**, nunca el transcript interno.
3. No invente radicados, SPOA ni sentencias. Use **[PENDIENTE DE VERIFICAR]** cuando falte ancla.
4. Un objetivo claro por turno (protección, impulso o seguimiento — no todo a la vez).
5. No copie al cliente el contenido crudo de Equipo interno.

---

## 2. Mapa del equipo (lenguaje de despacho)

| Área del despacho | Qué pedirle | Qué no pedirle |
|-------------------|-------------|----------------|
| **Coordinador del Caso** | Orquestar, resumir, pedir plan, hablar con usted y con la víctima | Que radique solo, que invente hechos |
| Cronología y hechos | Línea de tiempo, vacíos, hecho vs inferencia | Conclusiones de tipicidad definitivas |
| Tipicidad | Matriz preliminar de elementos del tipo | Sentencias inventadas, calificación firme |
| Ruta Ley 906 | Etapa, oportunidades, riesgo de archivo | Sustituir su criterio procesal |
| Representación de víctimas | Teoría del caso, no revictimización, intereses | Pieza final sin su revisión |
| Evidencia | Inventario, brechas, plan de recaudo | Afirmar cadena de custodia sin soporte |
| Audiencias | Guion / solicitudes de protección (según etapa) | Compromisos orales sin su OK |
| Redacción | Memoriales, derechos de petición, impulso | Radicar sin HITL |
| Seguimiento | Alertas de radicado, inactividad, términos | Monitoreo automático “oficial” sin datos |
| Calidad jurídica | Dictamen, tono, pendientes de verificación | Sustituir su firma |

> Nota técnica (pie): IDs internos = `coordinador_caso`, `analista_cronologia_hechos`, `analista_responsabilidad_tipicidad`, `analista_ruta_procesal`, `analista_representacion_victimas`, `analista_evidencia`, `analista_audiencias`, `redactor_documentos_juridicos`, `analista_seguimiento_procesal`, `analista_calidad_juridica` (9 especialistas + Gerente).

---

## 3. Ficha del caso (resumen)

**Laura R.** — VIF en Kennedy (Bogotá), hechos 12 jul 2026, denuncia verbal sin SPOA visible, mora 60+ días, luego derecho de petición sin respuesta.  
Texto completo: [`hechos_caso_laura_vif.md`](./hechos_caso_laura_vif.md).

Por qué tres actos: el producto no trae una sola plantilla con los 9 especialistas; tres planes realistas (protección VIF → impulso → seguimiento ante mora de petición) los ejercitan todos.

---

## 4. Acto 1 — Protección y teoría del caso (VIF)

### Objetivo pedagógico

Ver cómo el Gerente arma un **plan de equipo** (o consulta chat-first), muestra pedidos en **Equipo interno**, y deja piezas revisables antes de hablar con la víctima.

### Texto para pegar en `/abogado`

```
Acto 1 — Caso Laura R. (demo formación). Representamos a Laura R., víctima de
violencia intrafamiliar en Bogotá (Kennedy). Hechos del 12 de julio de 2026:
golpes, amenazas y retención del celular por su pareja Carlos M. Denuncia verbal
ante Policía el mismo día; aún sin SPOA. Datos sensibles autorizados.

Necesito: (1) cronología de hechos, (2) tipicidad preliminar VIF, (3) inventario
probatorio sensible, (4) teoría del caso centrada en la víctima sin revictimización,
y (5) guion de solicitudes de protección. Proponga plan de equipo y espere mi
aprobación. No invente radicados ni SPOA.
```

*(Opcional: adjuntar el anexo de hechos.)*

### Qué debe pasar en pantalla

1. Gerente recibe y puede pedir **plan** (plantilla VIF / protección) o consultar especialistas vía herramientas.
2. Si hay tarjeta de plan → **Aprobar y ejecutar** (no “Solicitar cambios” salvo que quiera enseñar rechazo).
3. Pestaña **Equipo interno**: pedidos claros (víctimas, tipicidad, evidencia, audiencias, calidad, etc.).
4. Puede aparecer borrador HITL (p. ej. plan probatorio) en **Bandeja** → Aprobar / Editar / Rechazar.

### Qué revisar usted

- Separación hecho / inferencia.
- Tono no revictimizante.
- Pendientes de verificación marcados.
- Nada “radicado” sin su firma.

### Errores comunes

- Aprobar el plan sin leer los pasos.
- Pedir al Gerente que “termine el caso” en un solo mensaje.
- Mostrar a la víctima el transcript de Equipo interno.

### Especialistas esperados (Acto 1)

Gerente, representación de víctimas, tipicidad, evidencia, audiencias (protección), calidad; a menudo también cronología.

---

## 5. Puente con la víctima (`/cliente`)

### Objetivo pedagógico

La víctima pregunta; el Gerente **borrador** una respuesta; usted aprueba en “Respuestas al cliente”; ella solo ve al Gerente.

### Mensaje modelo en `/cliente`

```
Doctora, ¿ya saben algo de mi denuncia? Tengo miedo de que él vuelva. ¿Qué sigue?
```

### Pasos en el escritorio

1. Abrir `/abogado` → pestaña **Borrador** / **Respuestas al cliente**.
2. Revisar el texto del Gerente (tono, promesas, datos sensibles).
3. **Aprobar** o **Editar** antes de que la víctima lo vea.
4. Confirmar en `/cliente` que el mensaje aprobado aparece.

### Errores comunes

- Aprobar outbound con radicados inventados.
- Responder desde Equipo interno “en crudo”.

---

## 6. Acto 2 — Impulso / anti-archivo ante Fiscalía

### Objetivo pedagógico

Completitud del expediente (radicado, poder, partes), plan **impulso**, y pieza de **redacción** + **seguimiento** con HITL. Enseñar también el tope operativo de tokens en demos largas (si aparece: acortar plan o desactivar tope solo en local).

### Texto para pegar

Primero, si el Gerente pide datos faltantes:

```
Completo el expediente para Acto 2: tengo el poder otorgado; soy apoderado
reconocido de la víctima. Partes: víctima Laura R. (CC 52.100.000), presunto
agresor Carlos M. (CC 79.200.000). Etapa: indagación. Radicado de trabajo
11001-60-00-2026-000001 [PENDIENTE DE VERIFICAR].
```

Luego el pedido de impulso:

```
Acto 2 — mismo caso Laura R. Han pasado más de 60 días desde la denuncia verbal
del 12 de julio de 2026 y aún no hay SPOA ni impulso visible. Necesito ruta Ley 906,
brechas probatorias, borrador de memorial de impulso ante Fiscalía, alertas de
seguimiento y control de calidad. Plan de equipo. No invente SPOA.
```

### Qué debe pasar en pantalla

1. Posible **bloqueo por completitud** (momento docente) → completar datos.
2. Plan plantilla **Impulso / anti-archivo** (cadena larga: cronología → tipicidad → ruta 906 → evidencia → redactor → seguimiento → calidad).
3. **Aprobar y ejecutar**.
4. Equipo interno con pedidos legibles.
5. Bandeja: memorial / control de calidad → aprobar.

### Qué revisar usted

- Radicado marcado como pendiente de verificar.
- Memorial: “BORRADOR — NO RADICAR SIN FIRMA”.
- Que el plan no se haya cortado a mitad (presupuesto operativo); si se corta, reintentar con plan más corto o presupuesto local en 0.

### Especialistas esperados (Acto 2)

Cronología, tipicidad, ruta 906, evidencia, **redactor**, **seguimiento**, calidad (+ Gerente).

---

## 7. Acto 3 — Impulso / seguimiento ante mora de petición

### Objetivo pedagógico

Cuando hay **derecho de petición sin respuesta**, el despacho permanece en la vía **penal**: nuevo memorial de impulso, alertas de seguimiento y control de calidad — **sin** abrir acción de tutela ni ruta constitucional.

### Texto para pegar

```
Acto 3 — mismo caso Laura R. (víctima; poder otorgado; apoderado reconocido).
Partes: Laura R. (CC 52.100.000) y Carlos M. (CC 79.200.000).
Radicado de trabajo 11001-60-00-2026-000001 [PENDIENTE DE VERIFICAR], etapa indagación.
Última actuación procesal: derecho de petición radicado ante Fiscalía hace 15 días
hábiles, sin respuesta a la fecha.

Necesito borrador de memorial de impulso / insistencia por silencio a la petición,
alertas de seguimiento procesal y control de calidad. Plan de equipo. No invente
sentencias ni radicados. No proponga acción de tutela.
```

### Qué debe pasar en pantalla

1. Si falta “última actuación”, el Gerente puede bloquear por completitud → aportarla.
2. Plan de **impulso / seguimiento** (vía penal): Gerente → redactor → seguimiento → calidad (ruta 906 / evidencia según plan).
3. Aprobar y ejecutar.
4. HITL de calidad / borrador → revisar memorial y alertas.

### Qué revisar usted

- La mora de petición se atiende con **impulso y seguimiento**, no con tutela.
- Juzgado / despacho y radicado siguen **[PENDIENTE DE VERIFICAR]** si no están certificados.
- No radicar el borrador sin firma.

### Especialistas esperados (Acto 3)

**Redactor**, **seguimiento**, calidad (+ Gerente; ruta 906 si el plan lo incluye).

---

## 8. Checklist de validación (Ricardo / formador)

Marque al cerrar la clase:

### Especialistas (9 + Gerente)

- [ ] Coordinador del Caso (`coordinador_caso`)
- [ ] Cronología (`analista_cronologia_hechos`)
- [ ] Tipicidad (`analista_responsabilidad_tipicidad`)
- [ ] Ruta 906 (`analista_ruta_procesal`)
- [ ] Víctimas (`analista_representacion_victimas`)
- [ ] Evidencia (`analista_evidencia`)
- [ ] Audiencias (`analista_audiencias`)
- [ ] Redacción (`redactor_documentos_juridicos`)
- [ ] Seguimiento (`analista_seguimiento_procesal`)
- [ ] Calidad (`analista_calidad_juridica`)

### HITL y cliente

- [ ] Al menos un borrador accionable pasó por Bandeja (Aprobar / Editar / Rechazar)
- [ ] Redactor / memoriales pasaron por revisión humana antes de “usarse”
- [ ] Mensaje de `/cliente` generó borrador outbound
- [ ] Outbound aprobado/editado; la víctima ve solo al Gerente
- [ ] No se inventaron radicados/SPOA en piezas aprobadas (o quedaron marcados pendientes)

### Pantallas

- [ ] Equipo interno mostró pedidos inteligibles (no solo IDs crudos)
- [ ] Plan(es) visibles con Aprobar / Solicitar cambios cuando aplica

---

## 9. Cierre para la clase — 5 tips

1. **Un objetivo por mensaje** (protección / impulso / seguimiento).
2. **Lea el plan** antes de aprobar; use “Solicitar cambios” si el alcance es excesivo.
3. **Equipo interno** es su tablero de delegación, no un chat con la víctima.
4. **HITL siempre** en memoriales, peticiones y respuestas al cliente.
5. **Pendientes de verificación** son una fortaleza del sistema, no un fallo: evitan alucinaciones.

---

## Referencias rápidas de demos internas

Corridas de referencia (local): sesiones `web:web-682f3e30` (Acto 1 + intentos), `web:demo-acto2-full2` (impulso completo). La demo histórica `web:demo-acto3-tutela` y el canvas IDE `laura-tres-actos-demo` (Acto 3 tutela) fueron **archivados/eliminados** — el producto ya no ofrece ruta constitucional; Acto 3 enseña impulso/seguimiento.

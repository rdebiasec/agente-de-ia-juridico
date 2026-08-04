# Reporte UX escritorio abogado (baseline y mejora)

## Alcance

- Pantalla auditada: `/abogado`
- Objetivo: reducir carga cognitiva, bajar riesgo de error en HITL y mejorar ergonomia operativa.

## Baseline previo (antes de cambios)

1. **Accion destructiva sobredimensionada**
   - Boton de reinicio duplicado y visualmente primario.
2. **Canal victima con legibilidad inconsistente**
   - Colores y tokens CSS mezclados que reducian contraste.
3. **Aprobacion hacia cliente con friccion insuficiente**
   - Flujo de "Aprobar y enviar" sin confirmacion proporcional al riesgo.
4. **Arquitectura de informacion fragmentada**
   - Tabs sin agrupacion por tarea (operar/supervisar/gestionar).
5. **Accesibilidad incompleta**
   - Tabs sin navegacion completa por teclado/roving.
6. **Polling tecnico no optimizado**
   - Actividad en vivo no se frenaba al salir del contexto, consumiendo ciclos innecesarios.

## Cambios aplicados

### P0 seguridad y legibilidad

- Se dejo **un solo camino principal** para reinicio visible (header).
- Se reforzo aprobacion de respuesta al cliente:
  - confirmacion explicita;
  - doble confirmacion cuando hay `quality_flags`.
- Se corrigio Canal victima en estilos oscuros coherentes.
- Se unifico feedback de error en canal victima a sistema de toast (sin `alert` bloqueante).

### IA de navegacion

- Se agrupo el panel en 3 zonas visibles:
  - **Operar**: Firma, Victima
  - **Supervisar**: Junta, Tecnico
  - **Gestionar**: Plazos, RAG
- Se renombraron tabs para que describan tarea y no solo modulo.

### Copy juridico

- Se elimino copy ambiguo de impersonacion:
  - ahora el desk habla de "registrar mensaje recibido de la victima" y auditoria explicita.
- Se reemplazo el badge heredado "Fase 1" por copy operativo:
  - "Borrador sujeto a su firma".

### Accesibilidad y ergonomia

- Tabs con `aria-controls` y `aria-labelledby` consistentes.
- Navegacion por teclado en tabs:
  - Flechas, Home/End, Enter/Espacio.
- Drawer con manejo de `Escape`, trampa de foco y retorno de foco.

### Refactor tecnico

- Nuevo modulo compartido: `static/desk-runtime.js`
  - utilidades de sesion;
  - event bus simple;
  - poller por tab/visibilidad.
- `Actividad` ahora se actualiza en vivo solo cuando la pestaña esta activa y la pagina visible.
- Modulos de desk reutilizan utilidades comunes para reducir duplicacion.

## Criterios de verificacion post-cambio

- El abogado identifica en menos de 2 minutos:
  - donde firmar;
  - donde revisar junta;
  - donde operar canal victima.
- No hay envio accidental facil a cliente con alertas de calidad.
- El cliente no ve informacion interna.
- El polling tecnico no se ejecuta fuera de contexto activo.

## QA ejecutado

- **Pruebas de regresion (PASS)**
  - `pytest tests/test_fase2_equipo_interno.py tests/test_fase3_cliente_front.py tests/test_fase1_triple_chat.py tests/test_mejora_triple_chat.py -q`
  - Resultado: `28 passed`.
- **Smoke local (PASS)**
  - `GET http://127.0.0.1:8000/abogado` → `200` + marcador `Operar · Firma`.
  - `GET http://127.0.0.1:8000/cliente` → `200` + marcador `Comenzar consulta`.
- **Smoke prod (pendiente de rollout de código)**
  - `GET https://agente-de-ia-juridico.onrender.com/abogado` → `200`, pero sin marcadores nuevos (`Operar · Firma`, `Registrar mensaje recibido de la víctima`).
  - `GET https://agente-de-ia-juridico.onrender.com/cliente` → `200`.
  - Conclusión: frontend local validado; producción aún no refleja este rediseño hasta publicar cambios.

## Archivos centrales intervenidos

- `static/desk/abogado.html`
- `static/chat.css`
- `static/chat.js`
- `static/workspace.js`
- `static/firma.js`
- `static/canal-victima.js`
- `static/equipo-interno.js`
- `static/desk-runtime.js`

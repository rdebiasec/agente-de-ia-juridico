# Udemy L04 — Model Settings — 2026-07-28 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #5  
**Decisión clase:** documentar gap · **código:** DEJAR QUIETO hasta `aprobado, ejecuta L04`  
**Gap:** no hay `ModelSettings` en `Agent(...)`; sí hay estratificación de **modelo** high-risk vs default

---

## 0. Veredicto

L04 enseña controlar el modelo por **config** (modelo, temperatura, esfuerzo), no solo por el prompt.  
Tu firma ya elige **modelo más fuerte** para redacción/tutela. Falta explicitar **temperatura baja** (y similares) en Agents de alto riesgo.  
Eso mejora determinismo de memoriales; no hace falta WebSocket.

---

## Mapa producto

| Control L04 | Hoy en el despacho | Dónde |
|---|---|---|
| Modelo default | `gpt-4o-mini` | `config.openai_model` |
| Modelo alto riesgo | `gpt-4o` | `openai_model_high_risk` + `_model_for_agent` |
| Fallback reintento | opcional | `openai_model_fallback` |
| `ModelSettings` (temp…) | **Ausente** en Agents | Gap |
| Presupuesto turns/tokens | Sí | settings + hooks runner |
| Chat transport | HTTPS | Correcto (no WebSocket) |

---

## High-level

> **Para L04: DEJAR QUIETO el runtime hoy.** La estratificación de modelo ya alinea costo/riesgo.  
> El ajuste de valor es añadir `ModelSettings` (temp baja en redactor/calidad/tutela) cuando digas `aprobado, ejecuta L04`.  
> No subir temperatura “para que suene más natural” en escritos legales.

| Ítem | Acción | Prioridad |
|---|---|---|
| `_model_for_agent` | Dejar | — |
| Añadir `ModelSettings` por rol | AJUSTE pendiente de aprobación | P0 producto |
| WebSocket | No | — |

---

## Cierre

Siguiente: **L05 RunContext**.

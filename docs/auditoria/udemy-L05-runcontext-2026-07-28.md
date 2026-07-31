# Udemy L05 — RunContext / RunContextWrapper — 2026-07-28 (clase formal)

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #6  
**Decisión:** AJUSTAR pendiente · anti-IDOR ya existe vía ContextVar  
**Comando:** `aprobado, ejecuta L05`

---

## 0. Veredicto

L05: pasar la “carpeta del caso” tipada al run (`context=`), no solo en el prompt.  
Hoy: `bind_active_session` + `resolve_expediente_id` (ContextVar) — defensa real anti-IDOR.  
Gap: no hay dataclass + `Runner.run(..., context=...)`; guardrails ven wrapper con `None`.  
Consentimiento 1581 sigue **fuera** del RunContext (gate de canal).

---

## High-level

> **DEJAR QUIETO el anti-IDOR actual.**  
> **AJUSTAR** cuando apruebes: dataclass (`session_id`, `expediente_id`, `channel`, `user_id`, flags) + cablear `context=` sin meter secrets/PII.  
> No romper ContextVar hasta que tools lean el context tipado.

---

## Cierre

Siguiente: **L07 Run Loop**.

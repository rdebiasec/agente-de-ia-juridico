# Udemy L02 — Lab Setup Codex + API Key — 2026-07-28

**Fase:** HECHO_CLASE  
**Orden pedagógico:** #2  
**Modo:** CLASE + mapa · **Decisión:** DEJAR QUIETO (sin rehacer lab)  
**Producto:** firma virtual — asistente de abogados

---

## 0. Veredicto

- **Qué es:** dejar el entorno listo (cuenta OpenAI, API key, IDE/repo) para poder correr agentes.
- **En este repo:** local (`./scripts/start-local.sh`) + Render (`OPENAI_API_KEY` en `render.yaml`) ya operativos.
- **¿Mejora desempeño?** Solo si el setup está roto; hoy no.
- **¿Tocar config?** No por L02. Ops: verificar que la key exista en local `.env` y en Render.

---

## 1. Clase (curso → despacho)

| Curso L02 | Aquí |
|---|---|
| Cuenta OpenAI + API key | `OPENAI_API_KEY` en env / Render |
| Codex + repo del lab | Este repo + Cursor (no rehacer lab Codex) |
| Validar setup temprano | `/chat` responde; sin key → fallback en `runner.py` |
| Free tier primero | Modelo vía `OPENAI_MODEL` / settings |

Sin API key el despacho **no explota**: `runner` usa `_fallback_response` (modo degradado).

---

## 2. Mapa

```
.dev / local          Render (prod)
  .env                  env Vars
  OPENAI_API_KEY   →    OPENAI_API_KEY
  OPENAI_MODEL          OPENAI_MODEL
  Postgres docker       Postgres managed
  ./scripts/start-local.sh   web service
```

| Pieza | Ruta |
|---|---|
| Settings | `src/config.py` (`openai_api_key`) |
| Deploy | `render.yaml` |
| Local | `scripts/start-local.sh`, `deploy/docker-compose.yml` |
| Uso key | `runner.py` `has_key` → Runner vs fallback |

---

## 3. High-level config

> **DEJAR QUIETO.** No rehacer el lab de Codex. El setup del asistente de abogados ya es local+Render. Solo ops: confirmar que `OPENAI_API_KEY` está presente donde corre el despacho.

| Ítem | Hoy | Acción |
|---|---|---|
| API key local/prod | Modelo env | Verificar ops; no código |
| Lab Codex del curso | N/A | No portar |
| Fallback sin key | Existe | Dejar (resiliencia) |

---

## 4. Qué NO hacer

- No commitear `.env` ni keys.
- No migrar a Bedrock “porque L28”.
- No depender de Codex del curso para este producto.

---

## 5. Cierre

- `cerrar L02, dejar quieto` — aplicado.  
- Siguiente: **L06** Basic Agents (qué es el POC).

<!-- config-version: 2; checksum: fb349ecfdf97c365 -->
# Fragmentos compartidos — prompts backoffice

**Versión:** 1.0 
**Uso:** copiar textualmente a `agente/prompts/agents/{especialista}.md` (el loader lee MD plano; no hay include runtime). 
**Porqué:** evita drift entre `notas_especialista` y `deliberacion_discutible` (H-005). 
**Al editar:** actualizar todos los especialistas que usen el bloque y bump `config-version`.

Sustituir `{AGENT_ID}` y `{DOMINIO}` por el id canónico y el dominio del especialista.

---

## notas_especialista

```markdown
## notas_especialista
Además de tu salida estructurada, elaboras **notas de trabajo propias** (bitácora de tu área).
No hablas con el abogado; tus notas las consume el Gerente y el expediente.

### Qué anotas (solo tu responsabilidad)
- Qué te pidió el Gerente (pedido / restricciones).
- Qué hechos usaste y su clasificación (confirmado|narrado|inferido|pendiente).
- Hallazgos clave de **tu** dominio ({DOMINIO}).
- Brechas, riesgos y `[PENDIENTE DE VERIFICAR]` de tu área.
- Recomendación de siguiente paso **para el Gerente** (no para el abogado en voz propia).

### Formato
- `autor`: `{AGENT_ID}`
- `tipo`: `analisis` | `inventario` | `alerta` | `borrador_interno`
- `resumen`: denso, sin relleno
- `hallazgos`: 1–7 bullets
- `pendientes`: bullets con dueño sugerido (`gerente` | `abogado` | tu área)
- `confidencialidad`: `normal` | `sensible` | `menor`

### Reglas
- No inventes. Si falta dato, anótalo como pendiente.
- No dupliques la bitácora maestra del Gerente; aporta el detalle de tu especialidad.
- Tus notas viajan en el campo `notas_trabajo` de tu schema.
```

---

## deliberacion_discutible

```markdown
## deliberacion_discutible
Al cerrar tu salida (prosa o notas), incluye siempre estos bloques para que el Gerente pueda repreguntar:
- `objeciones_o_riesgos`: 1–5 bullets (límites de tu análisis, riesgos de atipicidad/improcedencia, contradicciones).
- `preguntas_al_gerente`: 0–3 preguntas concretas (qué aclarar con el abogado u otra área).
- `confianza`: `baja` | `media` | `alta` sobre tus hallazgos principales.

Si el pedido viene con `modo=repregunta` o `contraste`, responde apuntando al `contexto_previo` y no repitas el informe completo sin más.
```

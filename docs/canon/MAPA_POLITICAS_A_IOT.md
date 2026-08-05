# Políticas del despacho → Input / Output / Tools

**Estado:** canónico (2026-08-05).  
**Fuente de enforcement:** `config/guardrails/agents/{agente}/{input|output|tools}.md` + `src/agents/sdk_guardrails.py` + HITL.  
**Los ids legacy `g1`…`g10` están deprecados:** solo alias de portal/progreso; no son frenos por sí solos.

| Policy id | Nombre | Capa I/O/T | Enforcement principal |
|---|---|---|---|
| `no_inventar` | No inventar | **output** (+ soft flag) | `poc_output` / `specialist_output` / `redactor_output` + `[PENDIENTE DE VERIFICAR]` |
| `pedir_faltantes` | Pedir datos faltantes | **input** | completeness gate + input guardrails |
| `hecho_vs_inferencia` | Separar hecho de inferencia | **output** | instrucciones + calidad |
| `hitl` | Revisión humana obligatoria | **tools** / HITL | `needs_approval` / plan aprobado (g4 legacy) |
| `no_revictimizar` | No revictimizar | **output** | política output + revisión calidad |
| `confidencialidad` | Confidencialidad / PII | **output** + **tools** | mask PII + tool in/out |
| `fuera_de_alcance` | Fuera de alcance | **input** | triage + input guardrail POC |
| `aviso_borrador` | Aviso de borrador | **output** (post) | `apply_output_guardrails` disclaimer |
| `terminos_906` | Oportunidad y términos Ley 906 | **output** (ruta/seguimiento) | prompts + skills de área |
| `integridad_probatoria` | Integridad probatoria | **output** + **tools** (evidencia) | política evidencia + skills |

Legacy alias: `g1`→`no_inventar` … `g10`→`integridad_probatoria` (ver `_shared/desk_policies.md`).

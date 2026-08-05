# Antes y ahora: políticas `g1`–`g10` → I/O/T

**Fecha:** 2026-08-05  
**Decisión:** I/O/T + SDK + HITL son la fuente de enforcement; `g*.md` quedan como **alias deprecados** (portal/progreso), no como frenos autónomos.

## Antes

| Qué | Cómo |
|---|---|
| Política | Diez archivos `config/guardrails/g1.md`…`g10.md` tratados como “canónicos” |
| Skills / prompts | Bullets `**g1:** …` y menciones `(g4)` en texto |
| Instrucciones slim | Hint que apuntaba a `g1..g10.md` como ids obligatorios |
| Seeds I/O | Concatenaban el bundle G1–G10 al input de cada agente |
| Riesgo | Doble fuente de verdad; el abogado auditaba `g*` creyendo que “aplicaban” solos |

## Ahora

| Qué | Cómo |
|---|---|
| Canónico | `config/guardrails/_shared/desk_policies.md` + mapa `docs/canon/MAPA_POLITICAS_A_IOT.md` |
| Enforcement | `config/guardrails/agents/{agente}/{input\|output\|tools}.md` + `sdk_guardrails` + HITL |
| Alias | `g1.md`…`g10.md` con `status: deprecated` y `policy_id` semántico (`no_inventar`, …) |
| Skills | Labels semánticos (`**No inventar:**`, …); sin ids `g*` |
| Slim hint | Nombres de política desk + puntero a I/O/T/SDK |
| Portal | Sigue pudiendo listar keys `g1`…`g10` como alias; el texto dice deprecado |

## Mapa rápido

`g1`→`no_inventar` · `g2`→`pedir_faltantes` · `g3`→`hecho_vs_inferencia` · `g4`→`hitl` · `g5`→`no_revictimizar` · `g6`→`confidencialidad` · `g7`→`fuera_de_alcance` · `g8`→`aviso_borrador` · `g9`→`terminos_906` · `g10`→`integridad_probatoria`

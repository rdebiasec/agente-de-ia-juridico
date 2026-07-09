# Baseline pre-producción — 2026-07-08

## Git

| Campo | Valor |
|-------|-------|
| Commit | `5a9f2251984b4bab779bae2722ecace7050ffbfc` |
| Mensaje | fix(auditoria): CSP en Render permita Tailwind y Font Awesome |
| Rama | `main` |

## URLs

| Entorno | URL |
|---------|-----|
| Render (app + auditoría) | https://agente-de-ia-juridico.onrender.com |
| Portal Render | https://agente-de-ia-juridico.onrender.com/auditoria/ |
| GitHub Pages | https://rdebiasec.github.io/agente-de-ia-juridico/ |

## Catálogo (build local `AUDIT_API_BASE=""`)

| Métrica | Valor |
|---------|------:|
| Reglas estrictas (guardrails) | 10 (g1–g10) |
| Agentes | 11 |
| Skills / guías | 90 |
| Pasos | 402 |
| Ítems auditables portal | 693 |

## Espejo skills

- Fuente: `.cursor/skills/*/SKILL.md`
- Espejo: `agente/skills/*/SKILL.md`
- Verificación: Capa 2 `validacion_sistema_completa.sh`

## Artefactos regenerados

```bash
AUDIT_API_BASE="" python scripts/generar_audit_portal.py
# → audit-portal/dist — 10 reglas, 11 agentes, 402 pasos (693 items auditable)
```

## Notas

- Dictamen 7 expertos previo (2026-07-07) es pre-g9/g10 formalizado en rubricas; re-ejecutar en este corte.
- Auditoría humana portal (693 ítems): pendiente despacho.

# Legal Audit Sync v2

Portal web para que la abogada líder audite el sistema penal-víctimas: **8 reglas estrictas**, **11 agentes** y **cada paso** de los 90 skills.

## Carpetas

| Carpeta | Uso |
|---|---|
| `site/` | Fuente local — edita `index.html` y `app.js` |
| `dist/` | Artefacto de despliegue — generado, no commitear |

## Uso local

```bash
./scripts/start-audit-portal.sh
```

O manualmente:

```bash
python scripts/generar_audit_portal.py
python -m http.server 8080 --directory audit-portal/dist
```

Abra `http://localhost:8080` (versión **v2.4** — si no ve cambios, recargue con Cmd+Shift+R).

## Manual de uso (sección 0)

La sección **0. Guía** incluye el manual completo para la abogada líder: jerarquía de 4 niveles, las 8 Reglas Estrictas con ejemplos, el flujo de los 11 agentes (3 gráficas) y el manual de auditoría en 7 pasos. Contenido dinámico desde `audit-data.json`.

## Qué audita la abogada

1. **Reglas Estrictas (Guardrails)** — límites técnicos del sistema
2. **11 agentes** — en 3 grupos: Coordinación, Especialistas, Calidad
3. **Pasos por skill** — cada skill muestra todos sus pasos (cantidad variable según catálogo); cada paso se aprueba, ajusta o marca pendiente

**Principio profesional:** La IA propone; la abogada revisa, ajusta y aprueba.

### Revertir decisiones

- **RESTABLECER** — borra la decisión y vuelve a estado inicial
- **APROBAR** otra vez sobre un ítem ya aprobado — también revierte a pendiente

Las decisiones se guardan en `localStorage` (`legal-audit-sync-v2`), incluyendo reglas y pasos agregados o eliminados por la abogada. Exporte el `.md` antes de limpiar el navegador.

## Despliegue (GitHub Pages)

Push a `main` → workflow `.github/workflows/deploy-audit-portal.yml` publica `dist/`.

Ver también [`DEPLOY.md`](../DEPLOY.md).

### Login (solo GitHub Pages)

| Entorno | Login |
|---|---|
| `localhost` | No — `auth-config.js` con `enabled: false` |
| GitHub Pages | Sí — si existe el secreto `AUDIT_PORTAL_PASSWORD` en Actions |

Secreto opcional: `AUDIT_PORTAL_USERNAME` (por defecto `auditor`). Sesión: 8 h en `sessionStorage`.

## Fuente de datos

- `agente/skills/*/SKILL.md`
- `docs/canon/lista-aprobacion-agentes-skills-pasos.md` (pasos operativos — corregidos tras auditoría gerencial)
- `docs/auditoria/auditoria-pasos-skills-gerencia-penal.md` (matriz con reasoning)
- `scripts/lib/pasos_gerencia_matrix.py` (fuente canónica de pasos variables)
- `scripts/lib/catalogo_aprobacion.py`

Regenerar tras cambios en pasos:

```bash
python scripts/auditar_pasos_skills_gerencia.py --apply --regenerar
python scripts/generar_audit_portal.py
```

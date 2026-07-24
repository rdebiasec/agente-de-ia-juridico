# Cuentas por abogado (siguiente paso de acceso)

## Hoy

- Chat web: un `SITE_USERNAME` + `SITE_PASSWORD` compartidos del despacho + consentimiento hard en login.
- Portal `/auditoria/`: mismo `SITE_PASSWORD` + **correo** + PIN personal (progreso y edits quedan atribuidos al correo).
- Idle de sesión: **60 minutos** por defecto (`SESSION_IDLE_MINUTES`).

## Puente inmediato (sin MFA aún)

Configurar en Render / `.env`:

```bash
# CSV de correos autorizados al editor de configuración
AUDIT_ALLOWED_EMAILS=abogada1@despacho.com,abogada2@despacho.com
```

Si la lista está vacía, cualquier correo válido + contraseña del despacho puede entrar (comportamiento anterior).

## Objetivo siguiente (no implementado aún)

1. Contraseña o SSO por abogado (no solo PIN sobre password compartido).
2. Offboarding: revocar correo en allowlist / desactivar usuario.
3. MFA opcional si el despacho lo exige.

Hasta entonces: trate `SITE_PASSWORD` como secreto de oficina y rote al salir alguien del equipo.

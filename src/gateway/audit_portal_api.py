"""API del portal de auditoría — login, consentimiento, PIN y persistencia."""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from src.auth.audit_gate import (
    AUDIT_COOKIE_NAME,
    audit_email_from_token,
    create_audit_session_token,
    is_valid_audit_email,
    normalize_audit_email,
    refresh_audit_session_token,
)
from src.auth.deps import cookie_secure, idle_seconds
from src.auth.gate import auth_enabled, verify_password
from src.compliance.pin import hash_pin, validate_pin_format, verify_pin
from src.compliance.policy import CURRENT_POLICY_VERSION, DATA_CONTROLLER
from src.config import Settings, get_settings
from src.middleware.rate_limit import check_rate_limit, reset_rate_limit
from src.gateway.audit_progress import (
    audit_progress_decision_count,
    audit_progress_regression_blocked,
    merge_audit_progress,
)
from src.storage import get_repository
from src.storage.models import AuditPortalAccessLog, AuditPortalUser, ComplianceConsent

router = APIRouter(prefix="/api/audit", tags=["audit-portal"])

LOGIN_RATE_MAX = 12
LOGIN_RATE_WINDOW = 900
PROGRESS_PUT_RATE_MAX = 90
PROGRESS_PUT_RATE_WINDOW = 60


def _config_write_file_enabled() -> bool:
    """En tests se puede desactivar exportación a disco (AUDIT_CONFIG_WRITE_FILE=0)."""
    import os

    return os.environ.get("AUDIT_CONFIG_WRITE_FILE", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


class AuditCredentialsBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1)


class AuditLoginBody(AuditCredentialsBody):
    pin: str | None = Field(default=None, max_length=8)
    new_pin: str | None = Field(default=None, max_length=8)
    accept_privacy: bool = False
    accept_sensitive_data: bool = False


class AuditProgressBody(BaseModel):
    version: int | None = None
    savedAt: str | None = None
    catalogGeneratedAt: str | None = None
    guardrails: dict = Field(default_factory=dict)
    agentes: dict = Field(default_factory=dict)
    guias: dict = Field(default_factory=dict)
    pasos: dict = Field(default_factory=dict)
    custom: dict | None = None


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    ua = (request.headers.get("user-agent") or "")[:500]
    return ip, ua


def _rate_key(request: Request, email: str = "") -> str:
    ip, _ = _client_meta(request)
    return f"audit-login:{ip or 'unknown'}:{normalize_audit_email(email)}"


def _log_access(
    request: Request,
    *,
    action: str,
    email: str | None = None,
    detail: str | None = None,
) -> None:
    ip, ua = _client_meta(request)
    get_repository().log_audit_portal_access(
        AuditPortalAccessLog(
            email=email,
            action=action,
            ip_address=ip,
            user_agent=ua,
            detail=detail,
        )
    )


def _apply_audit_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=AUDIT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=cookie_secure(settings),
        samesite="none" if cookie_secure(settings) else "lax",
        max_age=idle_seconds(settings),
        path="/",
    )


def _clear_audit_cookie(response: Response, settings: Settings) -> None:
    secure = cookie_secure(settings)
    samesite = "none" if secure else "lax"
    # set_cookie max_age=0 es más fiable que delete_cookie con SameSite=None en prod.
    response.set_cookie(
        key=AUDIT_COOKIE_NAME,
        value="",
        max_age=0,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


def _require_audit_email(
    request: Request,
    response: Response,
    audit_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
) -> str:
    if not auth_enabled(settings.site_password):
        raise HTTPException(
            status_code=503,
            detail="Auditoría no disponible: configure SITE_PASSWORD en el servidor.",
        )
    refreshed = refresh_audit_session_token(
        settings.session_secret,
        audit_session,
        idle_seconds=idle_seconds(settings),
    )
    if not refreshed:
        raise HTTPException(status_code=401, detail="Sesión de auditoría expirada o no autenticada.")
    _apply_audit_cookie(response, refreshed, settings)
    email = audit_email_from_token(
        settings.session_secret,
        refreshed,
        idle_seconds=idle_seconds(settings),
    )
    if not email:
        raise HTTPException(status_code=401, detail="Sesión de auditoría inválida.")
    request.state.audit_email = email
    return email


def _verify_site_password(settings: Settings, body: AuditCredentialsBody, request: Request) -> str:
    if not auth_enabled(settings.site_password):
        raise HTTPException(
            status_code=503,
            detail="Auditoría no disponible: configure SITE_PASSWORD en el servidor.",
        )
    email = normalize_audit_email(body.email)
    if not is_valid_audit_email(email):
        raise HTTPException(status_code=400, detail="Correo electrónico inválido.")
    if not check_rate_limit(_rate_key(request, email), max_attempts=LOGIN_RATE_MAX, window_seconds=LOGIN_RATE_WINDOW):
        _log_access(request, action="login_rate_limited", email=email)
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espere unos minutos.")
    if not verify_password(settings.site_password, body.password):
        _log_access(request, action="login_failed", email=email, detail="bad_password")
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    return email


def _record_consent(request: Request, email: str) -> None:
    ip, ua = _client_meta(request)
    get_repository().record_compliance_consent(
        ComplianceConsent(
            subject_key=email,
            context="audit_portal",
            policy_version=CURRENT_POLICY_VERSION,
            privacy_accepted=True,
            sensitive_data_ack=True,
            ip_address=ip,
            user_agent=ua,
        )
    )


@router.get("/policy")
async def audit_policy():
    return {
        "version": CURRENT_POLICY_VERSION,
        "controller": DATA_CONTROLLER,
        "privacy_url": "/legal/privacidad",
        "case_data_url": "/legal/tratamiento-datos-casos",
        "arco_email": DATA_CONTROLLER["contact_email"],
    }


@router.get("/catalog")
async def audit_catalog():
    """Catálogo vivo: agentes, skills, pasos y guardrails desde fuentes canónicas."""
    from src.gateway.audit_catalog import build_live_audit_catalog

    return build_live_audit_catalog()


@router.get("/config/catalog")
async def audit_config_catalog(email: str = Depends(_require_audit_email)):
    from src.config_store import list_catalog_items, seed_from_filesystem

    # Sembrar bajo demanda si la DB aún no tiene activos (p. ej. memoria en tests).
    try:
        seed_from_filesystem(author_email=email or "system@seed")
    except Exception:
        pass
    items = list_catalog_items()
    return {
        "ok": True,
        "counts": {k: len(v) for k, v in items.items()},
        "items": items,
    }


@router.get("/config/status")
async def audit_config_status():
    from src.compliance.skill_config import config_status
    from src.config_store import validate_config_store
    from src.storage import get_repository

    status = config_status()
    actives = get_repository().list_config_active()
    status["config_store"] = {
        "active_items": len(actives),
        "by_kind": {
            "prompt": sum(1 for a in actives if a.kind == "prompt"),
            "guardrail": sum(1 for a in actives if a.kind == "guardrail"),
            "skill": sum(1 for a in actives if a.kind == "skill"),
        },
        "validation_errors": validate_config_store(),
    }
    return status


@router.get("/config/events")
async def audit_config_events(email: str = Depends(_require_audit_email)):
    from src.compliance.skill_config import config_status, load_approved_config

    approved = load_approved_config()
    events = []
    if approved:
        events.append(
            {
                "action": "config_publish",
                "at": approved.get("published_at"),
                "by": approved.get("published_by"),
                "detail": f"v{approved.get('version')} checksum={approved.get('checksum')}",
            }
        )
    status = config_status()
    return {"status": status, "events": events}


class ConfigSaveBody(BaseModel):
    kind: str = Field(min_length=3, max_length=32)
    key: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    expected_version: int | None = None
    note: str = ""


class ConfigRestoreBody(BaseModel):
    version: int = Field(ge=1)
    note: str = ""


@router.get("/config/{kind}/{key}")
async def audit_config_get(kind: str, key: str, email: str = Depends(_require_audit_email)):
    from src.config_store import ConfigNotFoundError, ConfigValidationError, get_active_content

    try:
        return get_active_content(kind, key)
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/config/{kind}/{key}/versions")
async def audit_config_versions(
    kind: str, key: str, limit: int = 50, email: str = Depends(_require_audit_email)
):
    from src.config_store import ConfigValidationError, list_versions

    try:
        return {"kind": kind, "key": key, "versions": list_versions(kind, key, limit=min(limit, 100))}
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/config/{kind}/{key}/versions/{version}")
async def audit_config_version_detail(
    kind: str, key: str, version: int, email: str = Depends(_require_audit_email)
):
    from src.config_store import ConfigValidationError
    from src.config_store.paths import VALID_KINDS
    from src.storage import get_repository

    if kind not in VALID_KINDS:
        raise HTTPException(status_code=400, detail=f"kind inválido: {kind}")
    row = get_repository().get_config_version(kind, key, version)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No existe {kind}/{key} v{version}")
    return {
        "kind": row.kind,
        "key": row.key,
        "version": row.version,
        "content": row.content,
        "checksum": row.checksum,
        "author_email": row.author_email,
        "note": row.note,
        "created_at": row.created_at.isoformat(),
    }


@router.post("/config/save")
async def audit_config_save(
    request: Request,
    body: ConfigSaveBody,
    email: str = Depends(_require_audit_email),
):
    from src.config_store import (
        ConfigConflictError,
        ConfigValidationError,
        save_version,
    )
    from src.gateway.audit_catalog import refresh_runtime_catalog_caches

    try:
        saved = save_version(
            body.kind,
            body.key,
            body.content,
            author_email=email,
            note=body.note or "",
            expected_version=body.expected_version,
            write_file=_config_write_file_enabled(),
        )
    except ConfigConflictError as exc:
        _log_access(request, action="config_save_conflict", email=email, detail=str(exc)[:300])
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _log_access(
        request,
        action="config_save",
        email=email,
        detail=f"{body.kind}/{body.key} v{saved['version']}",
    )
    refresh_runtime_catalog_caches()
    return {"ok": True, **saved}


@router.post("/config/{kind}/{key}/restore")
async def audit_config_restore(
    kind: str,
    key: str,
    request: Request,
    body: ConfigRestoreBody,
    email: str = Depends(_require_audit_email),
):
    from src.config_store import (
        ConfigNotFoundError,
        ConfigValidationError,
        restore_version,
    )
    from src.gateway.audit_catalog import refresh_runtime_catalog_caches

    try:
        saved = restore_version(
            kind,
            key,
            body.version,
            author_email=email,
            note=body.note or "",
            write_file=_config_write_file_enabled(),
        )
    except ConfigNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfigValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _log_access(
        request,
        action="config_restore",
        email=email,
        detail=f"{kind}/{key} from_v{body.version} -> v{saved['version']}",
    )
    refresh_runtime_catalog_caches()
    return {"ok": True, **saved}


@router.post("/config/publish")
async def audit_config_publish(
    request: Request,
    email: str = Depends(_require_audit_email),
    body: AuditProgressBody | None = None,
):
    from src.compliance.skill_config import publish_skill_config, validate_runtime_skill_config
    from src.gateway.audit_catalog import build_live_audit_catalog, refresh_runtime_catalog_caches

    repo = get_repository()
    if body is not None:
        progress = body.model_dump()
    else:
        row = repo.get_audit_portal_progress(email)
        if row is None:
            raise HTTPException(status_code=400, detail="Sin progreso de auditoría para publicar.")
        progress = row.payload

    catalog = build_live_audit_catalog()
    try:
        published = publish_skill_config(catalog, progress, email=email)
    except ValueError as exc:
        _log_access(request, action="config_publish_rejected", email=email, detail=str(exc)[:500])
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    validation_errors = validate_runtime_skill_config()
    detail = f"v{published['version']} checksum={published.get('checksum')}"
    _log_access(request, action="config_publish", email=email, detail=detail)
    if validation_errors:
        _log_access(
            request,
            action="config_validate_warn",
            email=email,
            detail="; ".join(validation_errors[:5]),
        )

    refresh_runtime_catalog_caches()
    return {
        "ok": True,
        "published": {
            "version": published.get("version"),
            "published_at": published.get("published_at"),
            "checksum": published.get("checksum"),
            "validation_warnings": validation_errors,
        },
    }


@router.post("/prelogin")
async def audit_prelogin(
    body: AuditCredentialsBody,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    email = _verify_site_password(settings, body, request)
    repo = get_repository()
    user = repo.get_audit_portal_user(email)
    has_consent = repo.has_valid_compliance_consent(
        email, context="audit_portal", policy_version=CURRENT_POLICY_VERSION
    )
    return {
        "email": email,
        "needs_pin_setup": user is None,
        "needs_pin": user is not None,
        "needs_consent": not has_consent,
        "policy_version": CURRENT_POLICY_VERSION,
    }


@router.post("/login")
async def audit_login(
    body: AuditLoginBody,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    email = _verify_site_password(settings, body, request)
    repo = get_repository()
    user = repo.get_audit_portal_user(email)
    has_consent = repo.has_valid_compliance_consent(
        email, context="audit_portal", policy_version=CURRENT_POLICY_VERSION
    )

    if not has_consent:
        if not body.accept_privacy or not body.accept_sensitive_data:
            raise HTTPException(
                status_code=428,
                detail="Debe aceptar el aviso de privacidad y la autorización para datos de casos.",
            )
        _record_consent(request, email)

    if user is None:
        if not body.new_pin or not validate_pin_format(body.new_pin):
            raise HTTPException(
                status_code=428,
                detail="Primera vez: defina un PIN personal de 6 a 8 dígitos.",
            )
        repo.save_audit_portal_user(
            AuditPortalUser(email=email, pin_hash=hash_pin(body.new_pin))
        )
    else:
        if not body.pin or not verify_pin(body.pin, user.pin_hash):
            _log_access(request, action="login_failed", email=email, detail="bad_pin")
            raise HTTPException(status_code=401, detail="PIN incorrecto.")

    reset_rate_limit(_rate_key(request, email))
    token = create_audit_session_token(settings.session_secret, email)
    _apply_audit_cookie(response, token, settings)
    _log_access(request, action="login", email=email)
    return {"ok": True, "authenticated": True, "email": email, "policy_version": CURRENT_POLICY_VERSION}


@router.get("/session")
async def audit_session(
    request: Request,
    response: Response,
    audit_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
):
    if not auth_enabled(settings.site_password):
        return {"authenticated": False, "email": None, "auth_enabled": False}

    refreshed = refresh_audit_session_token(
        settings.session_secret,
        audit_session,
        idle_seconds=idle_seconds(settings),
    )
    if not refreshed:
        return {"authenticated": False, "email": None, "auth_enabled": True}
    _apply_audit_cookie(response, refreshed, settings)
    email = audit_email_from_token(
        settings.session_secret,
        refreshed,
        idle_seconds=idle_seconds(settings),
    )
    return {
        "authenticated": bool(email),
        "email": email,
        "auth_enabled": True,
        "policy_version": CURRENT_POLICY_VERSION,
    }


@router.post("/logout")
async def audit_logout(
    request: Request,
    response: Response,
    audit_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
):
    email = audit_email_from_token(
        settings.session_secret,
        audit_session,
        idle_seconds=idle_seconds(settings),
    ) if audit_session else None
    _clear_audit_cookie(response, settings)
    _log_access(request, action="logout", email=email)
    return {"ok": True}


@router.get("/progress")
async def get_audit_progress(request: Request, email: str = Depends(_require_audit_email)):
    repo = get_repository()
    row = repo.get_audit_portal_progress(email)
    if row is None:
        raise HTTPException(status_code=404, detail="Sin progreso guardado para este correo.")
    _log_access(request, action="get_progress", email=email)
    return row.payload


@router.put("/progress")
async def put_audit_progress(
    body: AuditProgressBody,
    request: Request,
    email: str = Depends(_require_audit_email),
):
    if not check_rate_limit(
        f"audit:put_progress:{email}",
        max_attempts=PROGRESS_PUT_RATE_MAX,
        window_seconds=PROGRESS_PUT_RATE_WINDOW,
    ):
        _log_access(request, action="put_progress_rate_limited", email=email)
        raise HTTPException(
            status_code=429,
            detail="Demasiados guardados seguidos. Espere un momento e intente de nuevo.",
        )
    repo = get_repository()
    payload = body.model_dump()
    existing = repo.get_audit_portal_progress(email)
    existing_payload = existing.payload if existing is not None else None
    merged = merge_audit_progress(existing_payload, payload)
    if existing is not None and audit_progress_regression_blocked(existing_payload, merged):
        existing_count = audit_progress_decision_count(existing_payload)
        incoming_count = audit_progress_decision_count(payload)
        _log_access(
            request,
            action="put_progress_rejected",
            email=email,
            detail=f"regression_blocked:{existing_count}->{incoming_count}",
        )
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede reducir el progreso guardado desde el navegador. "
                "Recargue la página o use «Borrar mi progreso» solo si desea empezar de cero."
            ),
        )
    row = repo.save_audit_portal_progress(email, merged)
    repo.append_audit_progress_history(email, merged)
    _log_access(
        request,
        action="put_progress",
        email=email,
        detail=f"decisions={audit_progress_decision_count(merged)}",
    )
    return {
        "ok": True,
        "email": row.email,
        "updated_at": row.updated_at.isoformat(),
        "decisions": audit_progress_decision_count(merged),
        "merged": audit_progress_decision_count(merged)
        > audit_progress_decision_count(payload),
    }


@router.delete("/progress")
async def delete_audit_progress(request: Request, email: str = Depends(_require_audit_email)):
    repo = get_repository()
    existing = repo.get_audit_portal_progress(email)
    if existing is None:
        raise HTTPException(status_code=404, detail="Sin progreso guardado para este correo.")
    # Instantánea previa al borrado ARCO — recuperable con restore_audit_progress.py
    repo.append_audit_progress_history(email, existing.payload)
    deleted = repo.delete_audit_portal_progress(email)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sin progreso guardado para este correo.")
    _log_access(
        request,
        action="delete_progress",
        email=email,
        detail=f"archived_decisions={audit_progress_decision_count(existing.payload)}",
    )
    return {"ok": True, "deleted": True, "archived": True}


@router.get("/execution-plans/dashboard")
async def audit_execution_plans_dashboard(
    request: Request,
    email: str = Depends(_require_audit_email),
):
    """KPIs de planes de ejecución para el portal (Fase 3)."""
    _log_access(request, action="execution_dashboard", email=email)
    return get_repository().execution_plan_stats()


@router.delete("/execution-plans")
async def audit_clear_execution_plans(
    request: Request,
    email: str = Depends(_require_audit_email),
):
    """Vacía el historial de planes de ejecución (contadores del dashboard)."""
    deleted = get_repository().clear_all_execution_plans()
    _log_access(
        request,
        action="execution_plans_reset",
        email=email,
        detail=f"deleted={deleted}",
    )
    return {"ok": True, "deleted": deleted}


@router.get("/execution-plans/{plan_id}/export.md")
async def audit_execution_plan_export(
    plan_id: str,
    request: Request,
    email: str = Depends(_require_audit_email),
):
    from fastapi.responses import Response

    from src.agents.plan_export import markdown_from_record

    record = get_repository().get_execution_plan(plan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    _log_access(request, action="execution_plan_export", email=email, detail=plan_id)
    md = markdown_from_record(record)
    return Response(
        content=md,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="plan-{plan_id}.md"'},
    )

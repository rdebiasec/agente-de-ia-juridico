"""FastAPI — gateway principal."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agents.runner import run_agent
from src.auth.dev import (
    dev_auto_login_allowed,
    dev_auto_login_redirect,
    login_html_with_dev_prefill,
    web_session_is_active,
)
from src.auth.deps import (
    apply_session_cookie,
    clear_session_cookie,
    get_web_subject_id,
    idle_seconds,
    optional_web_session,
    require_web_session,
    resolve_web_user_id,
)
from src.auth.gate import COOKIE_NAME, auth_enabled, create_session_token, is_session_active, parse_session_token, subject_id_from_token, verify_password
from src.config import Settings, get_settings
from src.gateway.reset import reset_conversation
from src.gateway.router import InboundMessage, handle_message
from src.gateway.trace import trace_store
from src.middleware.rate_limit import check_rate_limit, reset_rate_limit
from src.security import is_production, security_headers_for_path, validate_production_settings
from src.validation.probes import generate_probes
from src.validation.report import build_export_html, build_rules_only, build_session_report
from src.validation.rubric import CONNECTION_BLOCK, VALIDATION_BLOCKS, total_weight

if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    validate_production_settings(settings)

    # Inicializa el repositorio (ejecuta migraciones Alembic si hay Postgres).
    if settings.database_url:
        try:
            from src.storage import get_repository

            get_repository()
            logger.info("Repositorio Postgres inicializado (migraciones aplicadas)")
        except Exception:
            logger.exception("No se pudo inicializar el repositorio Postgres")

    # Scheduler de plazos (vigilancia de términos y recordatorios).
    try:
        from src.services.scheduler import start_scheduler

        start_scheduler()
    except Exception:
        logger.exception("No se pudo iniciar el scheduler")

    slack_task = None
    if settings.slack_bot_token and settings.slack_signing_secret:
        if not settings.slack_app_token:
            logger.warning(
                "Slack: bot+signing presentes pero falta SLACK_APP_TOKEN — "
                "Socket Mode no arrancará (usar xapp-…, no xoxb-…)"
            )
        try:
            from src.channels.slack_bot import start_slack_socket_mode

            slack_task = asyncio.create_task(start_slack_socket_mode())
            logger.info("Slack Socket Mode: tarea de conexión creada")
        except Exception as e:
            logger.warning("Slack Socket Mode no iniciado: %s", e)
    elif settings.slack_bot_token or settings.slack_signing_secret:
        logger.warning(
            "Slack parcial: se requieren SLACK_BOT_TOKEN y SLACK_SIGNING_SECRET juntos"
        )

    try:
        scripts = settings.project_root / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from generar_audit_portal import ensure_audit_portal_artifacts

        ensure_audit_portal_artifacts(full_if_missing=True)
        logger.info("Portal de auditoría: catálogo sincronizado con fuentes canónicas")
    except Exception:
        logger.exception("Portal de auditoría: no se pudo regenerar catálogo al arranque")

    try:
        from src.compliance.skill_config import validate_runtime_skill_config
        from src.storage import get_repository
        from src.storage.models import AuditPortalAccessLog

        cfg_errors = validate_runtime_skill_config()
        if cfg_errors:
            logger.warning("Validación config skills: %s", "; ".join(cfg_errors[:5]))
            get_repository().log_audit_portal_access(
                AuditPortalAccessLog(
                    email=None,
                    action="config_validate_failed",
                    detail="; ".join(cfg_errors[:8]),
                )
            )
        else:
            get_repository().log_audit_portal_access(
                AuditPortalAccessLog(
                    email=None,
                    action="config_validate_ok",
                    detail="startup",
                )
            )
    except Exception:
        logger.exception("No se pudo validar configuración de skills al arranque")

    yield
    if slack_task:
        slack_task.cancel()
    try:
        from src.services.scheduler import stop_scheduler

        stop_scheduler()
    except Exception:
        logger.exception("Error al detener el scheduler")


# En Render/producción no exponer OpenAPI (superficie de ataque innecesaria).
_DISABLE_API_DOCS = bool(__import__("os").environ.get("RENDER"))
app = FastAPI(
    title="Agente Jurídico",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if _DISABLE_API_DOCS else "/docs",
    redoc_url=None if _DISABLE_API_DOCS else "/redoc",
    openapi_url=None if _DISABLE_API_DOCS else "/openapi.json",
)

WEB_LOGIN_RATE_MAX = 12
WEB_LOGIN_RATE_WINDOW = 900
CHAT_PLAN_RATE_MAX = 20
CHAT_PLAN_RATE_WINDOW = 900


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    if request.client:
        return request.client.host
    return "unknown"


def _web_login_rate_key(request: Request) -> str:
    return f"web-login:{_client_ip(request)}"


def _chat_plan_rate_key(subject_id: str) -> str:
    return f"chat-plan:{subject_id}"


def _audit_cors_origins() -> list[str]:
    import os

    origins: list[str] = []
    raw = os.environ.get("AUDIT_CORS_ORIGINS", "").strip()
    if raw:
        origins.extend(origin.strip() for origin in raw.split(",") if origin.strip())
    else:
        origins.extend(
            [
                "https://rdebiasec.github.io",
                "http://127.0.0.1:8080",
                "http://localhost:8080",
            ]
        )
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
    if render_url and render_url not in origins:
        origins.append(render_url)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_audit_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Last-Event-ID"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    if is_production(get_settings()):
        for header, value in security_headers_for_path(request.url.path).items():
            response.headers.setdefault(header, value)
    return response


from src.gateway.audit_portal_api import router as audit_portal_router
from src.gateway.compliance_api import router as compliance_router
from src.gateway.firma_api import router as firma_router
from src.gateway.slack_interactivity import router as slack_router
from src.gateway.support_api import router as support_router
from src.gateway.twilio_webhook import router as twilio_router

app.include_router(audit_portal_router)
app.include_router(compliance_router)
app.include_router(firma_router)
app.include_router(slack_router)
app.include_router(support_router)
app.include_router(twilio_router)

_static_dir = get_settings().project_root / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

_audit_portal_dir = get_settings().project_root / "audit-portal" / "dist"
if _audit_portal_dir.is_dir():
    app.mount(
        "/auditoria",
        StaticFiles(directory=_audit_portal_dir, html=True),
        name="auditoria",
    )


def _auth_redirect_if_needed(request: Request, settings: Settings) -> RedirectResponse | None:
    if auth_enabled(settings.site_password):
        if web_session_is_active(request, settings):
            return None
        auto = dev_auto_login_redirect(request, settings, next_url=str(request.url.path))
        if auto:
            return auto
        return RedirectResponse(url="/login", status_code=302)
    return None


@app.get("/login")
async def login_page(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    if web_session_is_active(request, settings):
        return RedirectResponse(url="/", status_code=302)

    if "login_error" not in request.query_params and "expired" not in request.query_params:
        auto = dev_auto_login_redirect(request, settings, next_url="/")
        if auto:
            return auto

    login = _static_dir / "login.html"
    if not login.is_file():
        return RedirectResponse(url="/", status_code=302)

    if dev_auto_login_allowed(settings):
        html = login_html_with_dev_prefill(login.read_text(encoding="utf-8"), settings)
        return HTMLResponse(html)

    return FileResponse(login)


@app.get("/")
async def root_redirect(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    return RedirectResponse(url="/abogado", status_code=302)


@app.get("/abogado")
async def abogado_desk(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    page = _static_dir / "desk" / "abogado.html"
    if page.is_file():
        return FileResponse(page)
    index = _static_dir / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Escritorio del abogado no encontrado.")


@app.get("/soporte")
async def soporte_desk(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    page = _static_dir / "desk" / "soporte.html"
    if not page.is_file():
        raise HTTPException(status_code=404, detail="Consola de soporte no encontrada.")
    return FileResponse(page)


@app.get("/chat")
async def chat_page_legacy(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    """Compatibilidad: redirige al escritorio del abogado."""
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    return RedirectResponse(url="/abogado", status_code=302)


@app.get("/help")
async def help_page(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    manual = _static_dir / "GUIA_FASE1.html"
    if manual.is_file():
        return FileResponse(manual)
    raise HTTPException(status_code=404, detail="Manual no encontrado")


@app.get("/legal/privacidad")
async def legal_privacidad_page():
    page = _static_dir / "legal" / "privacidad.html"
    if page.is_file():
        return FileResponse(page)
    raise HTTPException(status_code=404, detail="Aviso de privacidad no encontrado.")


@app.get("/legal/tratamiento-datos-casos")
async def legal_case_data_page():
    page = _static_dir / "legal" / "tratamiento-datos-casos.html"
    if page.is_file():
        return FileResponse(page)
    raise HTTPException(status_code=404, detail="Documento no encontrado.")


@app.get("/legal/terminos")
async def legal_terminos_page():
    page = _static_dir / "legal" / "terminos.html"
    if page.is_file():
        return FileResponse(page)
    raise HTTPException(status_code=404, detail="Términos no encontrados.")


@app.get("/auth/status")
async def auth_status(
    request: Request,
    response: Response,
    authenticated: bool = Depends(optional_web_session),
    settings: Settings = Depends(get_settings),
):
    enabled = auth_enabled(settings.site_password)
    username = None
    subject_id = None
    if enabled and authenticated:
        token = request.cookies.get(COOKIE_NAME)
        data = parse_session_token(settings.session_secret, token) if token else None
        username = (data or {}).get("username") or settings.site_username
        subject_id = subject_id_from_token(settings.session_secret, token)
    return {
        "auth_enabled": enabled,
        "authenticated": authenticated if enabled else True,
        "idle_minutes": settings.session_idle_minutes,
        "username": username,
        "subject_id": subject_id,
    }


@app.post("/auth/login")
async def auth_login(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    content_type = request.headers.get("content-type", "")
    wants_redirect = "application/json" not in content_type

    try:
        if "application/json" in content_type:
            body = await request.json()
            username = str(body.get("username", ""))
            password = str(body.get("password", ""))
            from src.compliance.consent import extract_consent_flags

            accept_privacy, accept_cases = extract_consent_flags(body if isinstance(body, dict) else {})
        else:
            form = await request.form()
            username = str(form.get("username", ""))
            password = str(form.get("password", ""))
            from src.compliance.consent import extract_consent_flags

            accept_privacy, accept_cases = extract_consent_flags(dict(form))
    except Exception as exc:
        logger.exception("Fallo al parsear login")
        if wants_redirect:
            return RedirectResponse(url="/login?login_error=1", status_code=302)
        raise HTTPException(status_code=400, detail="Datos de login inválidos.") from exc

    if not auth_enabled(settings.site_password):
        if wants_redirect:
            return RedirectResponse(url="/", status_code=302)
        return {"ok": True, "auth_enabled": False}

    if not check_rate_limit(
        _web_login_rate_key(request),
        max_attempts=WEB_LOGIN_RATE_MAX,
        window_seconds=WEB_LOGIN_RATE_WINDOW,
    ):
        logger.warning("Login rate limited desde IP %s", _client_ip(request))
        if wants_redirect:
            return RedirectResponse(url="/login?login_error=1", status_code=302)
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espere unos minutos.")

    credentials_ok = username == settings.site_username and verify_password(
        settings.site_password, password
    )
    if not credentials_ok:
        if wants_redirect:
            return RedirectResponse(url="/login?login_error=1", status_code=302)
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    if not accept_privacy or not accept_cases:
        if wants_redirect:
            return RedirectResponse(url="/login?consent_error=1", status_code=302)
        raise HTTPException(
            status_code=428,
            detail="Debe aceptar el aviso de privacidad y la autorización de datos de casos.",
        )

    from src.compliance.consent import record_web_chat_consent

    record_web_chat_consent(username=username, request=request)

    reset_rate_limit(_web_login_rate_key(request))
    token = create_session_token(settings.session_secret, username=username)
    if wants_redirect:
        redirect = RedirectResponse(url="/", status_code=302)
        apply_session_cookie(redirect, token, settings)
        return redirect

    apply_session_cookie(response, token, settings)
    return {"ok": True, "idle_minutes": settings.session_idle_minutes}


@app.post("/auth/logout")
async def auth_logout(
    response: Response,
    settings: Settings = Depends(get_settings),
):
    clear_session_cookie(response, settings)
    return {"ok": True}


@app.post("/auth/heartbeat")
async def auth_heartbeat(
    authenticated: bool = Depends(optional_web_session),
    settings: Settings = Depends(get_settings),
):
    if not auth_enabled(settings.site_password):
        return {"ok": True}
    if not authenticated:
        raise HTTPException(status_code=401, detail="Sesión expirada.")
    return {"ok": True, "idle_minutes": settings.session_idle_minutes}


class ChatRequest(BaseModel):
    message: str
    channel: str = "web"
    user_id: str = "test"


class ChatResponse(BaseModel):
    text: str
    agent: str
    pending_review: bool = False
    draft_id: str | None = None
    trace: dict | None = None
    plan_id: str | None = None


class ChatPlanRequest(BaseModel):
    message: str
    channel: str = "web"
    user_id: str = "web"


class ChatPlanResponse(BaseModel):
    plan: dict
    plan_id: str
    status: str


class ChatPlanActionRequest(BaseModel):
    user_id: str = "web"
    reason: str = ""
    remember_pattern: bool = False


class ChatPlanExecuteResponse(BaseModel):
    text: str
    agent: str
    pending_review: bool = False
    draft_id: str | None = None
    trace: dict | None = None
    session_id: str
    plan_id: str
    plan: dict | None = None


class ChatResetRequest(BaseModel):
    channel: str = "web"
    user_id: str = "web"


class ChatResetResponse(BaseModel):
    ok: bool = True
    session_id: str
    cleared_messages: bool = False
    cleared_traces: int = 0


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[dict]
    traces: list[dict]
    expediente: dict | None = None

class TraceDebugResponse(BaseModel):
    session_id: str
    traces: list[dict]


@app.get("/health")
async def health():
    settings = get_settings()
    from src.channels.slack_status import slack_health_flags
    from src.services.twilio_notify import twilio_habilitado

    slack_flags = slack_health_flags()
    from src.compliance.crypto_at_rest import status_payload as crypto_status

    payload = {
        "status": "ok",
        "modo": "firma",
        "environment": "production" if is_production(settings) else "development",
        "openai_configured": bool(settings.openai_api_key),
        "slack_configured": slack_flags["slack_configured"],
        "slack_app_token_configured": slack_flags["slack_app_token_configured"],
        "slack_socket_started": slack_flags["slack_socket_started"],
        "twilio_configured": twilio_habilitado(),
        "persistencia": "postgres" if settings.database_url else "memoria",
        "web_auth_enabled": auth_enabled(settings.site_password),
        "dev_auto_login": dev_auto_login_allowed(settings) if auth_enabled(settings.site_password) else False,
        **crypto_status(),
    }
    return payload


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_web_session)])
async def chat(
    req: ChatRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    result = await handle_message(
        InboundMessage(channel=req.channel, user_id=uid, text=req.message)
    )
    return ChatResponse(
        **{k: result[k] for k in ("text", "agent", "pending_review", "draft_id", "trace") if k in result}
    )


def _plan_session_id(channel: str, user_id: str) -> str:
    return f"{channel}:{user_id}"


@app.post("/chat/plan", response_model=ChatPlanResponse, dependencies=[Depends(require_web_session)])
async def chat_create_plan(
    req: ChatPlanRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    from src.agents.planner import create_execution_plan

    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    if not uid or len(uid) > 120:
        raise HTTPException(status_code=400, detail="user_id inválido.")
    if not check_rate_limit(
        _chat_plan_rate_key(uid),
        max_attempts=CHAT_PLAN_RATE_MAX,
        window_seconds=CHAT_PLAN_RATE_WINDOW,
    ):
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes de plan. Espere unos minutos.")
    session_id = _plan_session_id(req.channel, uid)
    plan, err = create_execution_plan(
        message=req.message,
        channel=req.channel,
        session_id=session_id,
        user_id=uid,
    )
    if err or not plan:
        raise HTTPException(status_code=400, detail=err or "No se pudo generar el plan.")
    return ChatPlanResponse(plan=plan.to_dict(), plan_id=plan.plan_id, status=plan.status)


@app.get("/chat/plan/{plan_id}", dependencies=[Depends(require_web_session)])
async def chat_get_plan(plan_id: str, uid: str = Depends(get_web_subject_id)):
    from src.agents.planner import get_plan

    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    if plan.initiator_user_id != uid:
        raise HTTPException(status_code=403, detail="No autorizado.")
    return {"plan": plan.to_dict(), "plan_id": plan.plan_id, "status": plan.status}


@app.post("/chat/plan/{plan_id}/approve", dependencies=[Depends(require_web_session)])
async def chat_approve_plan(
    plan_id: str,
    req: ChatPlanActionRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    from src.agents.planner import approve_plan

    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    plan, err = approve_plan(plan_id, uid, remember_pattern=req.remember_pattern)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True, "plan": plan.to_dict() if plan else {}, "status": plan.status if plan else ""}


@app.post("/chat/plan/{plan_id}/reject", dependencies=[Depends(require_web_session)])
async def chat_reject_plan(
    plan_id: str,
    req: ChatPlanActionRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    from src.agents.planner import reject_plan

    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    plan, err = reject_plan(plan_id, uid, req.reason or "")
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"ok": True, "plan": plan.to_dict() if plan else {}, "status": plan.status if plan else ""}


@app.post("/chat/plan/{plan_id}/approve-and-execute", response_model=ChatPlanExecuteResponse, dependencies=[Depends(require_web_session)])
async def chat_approve_and_execute(
    plan_id: str,
    req: ChatPlanActionRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    from src.agents.plan_executor import approve_and_execute
    from src.gateway.trace import trace_store

    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    result = await approve_and_execute(plan_id, uid)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    if result.get("trace"):
        trace_store.add(result["session_id"], result["trace"])
    return ChatPlanExecuteResponse(
        text=result["text"],
        agent=result["agent"],
        pending_review=result.get("pending_review", False),
        draft_id=result.get("draft_id"),
        trace=result.get("trace"),
        session_id=result["session_id"],
        plan_id=result["plan_id"],
        plan=result.get("plan"),
    )


@app.post("/chat/plan/{plan_id}/execute", status_code=202, dependencies=[Depends(require_web_session)])
async def chat_execute_plan(
    plan_id: str,
    req: ChatPlanActionRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    """Inicia ejecución async del plan aprobado (Fase 2)."""
    from src.agents.plan_executor import schedule_execute_async

    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    if not check_rate_limit(
        _chat_plan_rate_key(uid),
        max_attempts=CHAT_PLAN_RATE_MAX,
        window_seconds=CHAT_PLAN_RATE_WINDOW,
    ):
        raise HTTPException(status_code=429, detail="Demasiadas ejecuciones de plan. Espere unos minutos.")
    result = await schedule_execute_async(plan_id, uid)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result


@app.get("/chat/plan/{plan_id}/events", dependencies=[Depends(require_web_session)])
async def chat_plan_events(
    plan_id: str,
    request: Request,
    uid: str = Depends(get_web_subject_id),
):
    """SSE — eventos en vivo de ejecución del plan."""
    from src.agents.plan_events import PlanEventBroker
    from src.storage import get_repository

    record = get_repository().get_execution_plan(plan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    plan_payload = record.payload or {}
    plan_user = plan_payload.get("initiator_user_id", "")
    if plan_user != uid:
        raise HTTPException(status_code=403, detail="No autorizado.")

    raw_last = (
        request.headers.get("last-event-id")
        or request.query_params.get("last_event_id")
        or "0"
    )
    try:
        after_seq = int(raw_last)
    except ValueError:
        after_seq = 0

    broker = PlanEventBroker.get()
    persisted = plan_payload.get("stream_events") or []
    await broker.seed_history(plan_id, persisted)

    async def event_stream():
        async for event in broker.subscribe(plan_id, after_seq=after_seq):
            yield f"id: {event['seq']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/chat/plan/{plan_id}/result", dependencies=[Depends(require_web_session)])
async def chat_plan_result(plan_id: str, uid: str = Depends(get_web_subject_id)):
    from src.agents.plan_executor import get_plan_result

    result = get_plan_result(plan_id, uid)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result["error"])
    return result


def _plan_markdown_response(record, plan) -> Response:
    from src.agents.plan_export import markdown_from_record

    md = markdown_from_record(record)
    filename = f"plan-{plan.plan_id}.md"
    return Response(
        content=md,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/chat/plan/{plan_id}/export.md", dependencies=[Depends(require_web_session)])
async def chat_plan_export_md(plan_id: str, uid: str = Depends(get_web_subject_id)):
    """Export Markdown del plan + I/O (Fase 3)."""
    from src.agents.planner import get_plan
    from src.storage import get_repository

    record = get_repository().get_execution_plan(plan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    plan = get_plan(plan_id)
    if not plan or plan.initiator_user_id != uid:
        raise HTTPException(status_code=403, detail="No autorizado.")
    return _plan_markdown_response(record, plan)


@app.post("/chat/reset", response_model=ChatResetResponse, dependencies=[Depends(require_web_session)])
async def chat_reset(
    req: ChatResetRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    """Reinicia historial del agente, trazas y expediente sin esperar idle de sesión."""
    if req.channel != "web":
        raise HTTPException(status_code=400, detail="Solo se admite reinicio en canal web.")
    user_id = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    if not user_id or len(user_id) > 120:
        raise HTTPException(status_code=400, detail="user_id inválido.")
    try:
        result = reset_conversation(channel=req.channel, user_id=user_id)
    except Exception as exc:
        logger.exception("Fallo al reiniciar chat para web:%s", user_id)
        msg = str(exc).lower()
        if "connection refused" in msg or "operationalerror" in type(exc).__name__.lower():
            raise HTTPException(
                status_code=503,
                detail="Base de datos no disponible. Ejecute ./scripts/start-local.sh o ./scripts/local_db.sh.",
            ) from exc
        raise HTTPException(status_code=500, detail="No se pudo reiniciar la conversación.") from exc
    return ChatResetResponse(**result)


@app.get("/chat/history", response_model=ChatHistoryResponse, dependencies=[Depends(require_web_session)])
async def chat_history(channel: str = "web", uid: str = Depends(get_web_subject_id)):
    """Historial de conversación, trazas y expediente persistidos para la sesión web."""
    if channel != "web":
        raise HTTPException(status_code=400, detail="Solo canal web.")
    if not uid or len(uid) > 120:
        raise HTTPException(status_code=400, detail="user_id inválido.")
    session_id = f"{channel}:{uid}"
    from src.gateway.expediente import expediente_store
    from src.storage import get_repository

    chat = get_repository().get_chat_session(session_id)
    exp = expediente_store.get(session_id)
    raw_messages = list(chat.messages) if chat else []
    messages = []
    for msg in raw_messages:
        role = str(msg.get("role") or "user")
        content = msg.get("content", "")
        from src.gateway.message_content import normalize_message_content, strip_runner_injected_context

        text = normalize_message_content(content)
        if role == "user":
            text = strip_runner_injected_context(text)
        messages.append({**msg, "content": text})
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        traces=trace_store.get(session_id, limit=40),
        expediente=exp.to_dict() if exp else None,
    )


def _validate_trace_session_id(session_id: str) -> str:
    raw = (session_id or "").strip()
    if not raw or len(raw) > 120:
        raise HTTPException(status_code=400, detail="session_id inválido.")
    if not raw.startswith("web:"):
        raise HTTPException(status_code=403, detail="Solo se permite traza interna de sesiones web.")
    return raw


@app.get("/debug/trace/{session_id}", response_model=TraceDebugResponse, dependencies=[Depends(require_web_session)])
async def debug_trace(session_id: str, limit: int = 20, uid: str = Depends(get_web_subject_id)):
    """Consulta traza interna del flujo de agentes por sesión web autenticada."""
    sid = _validate_trace_session_id(session_id)
    if sid != f"web:{uid}":
        raise HTTPException(status_code=403, detail="No autorizado para esta sesión.")
    max_limit = max(1, min(limit, 100))
    traces = trace_store.get(sid, limit=max_limit)
    return TraceDebugResponse(session_id=sid, traces=traces)


class GenerateProbesRequest(BaseModel):
    user_id: str = "web"
    blocks: list[str] | None = None
    probes_per_block: int = 2


@app.get("/validation/rubric", dependencies=[Depends(require_web_session)])
async def validation_rubric():
    """Pesos y metadatos de la rúbrica Fase 0."""
    return {
        "total_weight": total_weight(),
        "connection": CONNECTION_BLOCK,
        "blocks": [
            {
                "id": b["id"],
                "title": b["title"],
                "weight": b["weight"],
            }
            for b in VALIDATION_BLOCKS
        ],
    }


@app.post("/validation/generate-probes", dependencies=[Depends(require_web_session)])
async def validation_generate_probes(
    req: GenerateProbesRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    uid = resolve_web_user_id(
        settings,
        request.cookies.get(COOKIE_NAME),
        client_fallback=req.user_id,
        response=response,
    )
    try:
        return await generate_probes(
            user_id=uid,
            blocks=req.blocks,
            probes_per_block=req.probes_per_block,
        )
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e


class SessionReportRequest(BaseModel):
    user_id: str = "web"
    session: dict
    include_llm: bool = True


class SessionExportRequest(BaseModel):
    user_id: str = "web"
    session: dict
    report: dict | None = None


class SessionRulesRequest(BaseModel):
    session: dict


@app.post("/validation/session-rules", dependencies=[Depends(require_web_session)])
async def validation_session_rules(req: SessionRulesRequest):
    """Conclusiones por reglas sin LLM — refresh automático del panel."""
    return build_rules_only(req.session)


@app.post("/validation/session-report", dependencies=[Depends(require_web_session)])
async def validation_session_report(req: SessionReportRequest):
    report = await build_session_report(req.session, include_llm=req.include_llm)
    return report


@app.post("/validation/session-export", dependencies=[Depends(require_web_session)])
async def validation_session_export(req: SessionExportRequest):
    from fastapi.responses import Response

    if req.report:
        report = req.report
    else:
        report = await build_session_report(req.session, include_llm=False)
    html = build_export_html(req.session, report)
    filename = f"reporte-fase0-{req.session.get('sessionId', 'sesion')}.doc"
    return Response(
        content=html.encode("utf-8"),
        media_type="application/msword",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def main():
    import uvicorn

    settings = get_settings()
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=False)


if __name__ == "__main__":
    main()

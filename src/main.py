"""FastAPI — gateway principal."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agents.runner import run_agent
from src.auth.deps import (
    apply_session_cookie,
    clear_session_cookie,
    idle_seconds,
    optional_web_session,
    require_web_session,
)
from src.auth.gate import COOKIE_NAME, auth_enabled, create_session_token, is_session_active, parse_session_token, verify_password
from src.channels.whatsapp_webhook import router as whatsapp_router
from src.config import Settings, get_settings
from src.gateway.router import InboundMessage, handle_message
from src.validation.probes import generate_probes
from src.validation.report import build_export_html, build_rules_only, build_session_report
from src.validation.rubric import CONNECTION_BLOCK, VALIDATION_BLOCKS, total_weight

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    slack_task = None
    if settings.slack_bot_token and settings.slack_signing_secret:
        try:
            from src.channels.slack_bot import start_slack_socket_mode

            slack_task = asyncio.create_task(start_slack_socket_mode())
            logger.info("Slack Socket Mode iniciado")
        except Exception as e:
            logger.warning("Slack Socket Mode no iniciado: %s", e)
    yield
    if slack_task:
        slack_task.cancel()


app = FastAPI(title="Agente Jurídico", version="0.1.0", lifespan=lifespan)
app.include_router(whatsapp_router)

_static_dir = get_settings().project_root / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


def _auth_redirect_if_needed(request: Request, settings: Settings) -> RedirectResponse | None:
    if auth_enabled(settings.site_password):
        token = request.cookies.get(COOKIE_NAME)
        if not is_session_active(
            settings.session_secret,
            token,
            idle_seconds=idle_seconds(settings),
        ):
            return RedirectResponse(url="/login", status_code=302)
    return None


@app.get("/login")
async def login_page():
    login = _static_dir / "login.html"
    if login.is_file():
        return FileResponse(login)
    return RedirectResponse(url="/", status_code=302)


@app.get("/")
async def chat_page(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    index = _static_dir / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {"message": "Agente Jurídico API — use POST /chat"}


@app.get("/help")
async def help_page(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    redirect = _auth_redirect_if_needed(request, settings)
    if redirect:
        return redirect
    manual = _static_dir / "GUIA_FASE0.html"
    if manual.is_file():
        return FileResponse(manual)
    raise HTTPException(status_code=404, detail="Manual no encontrado")


@app.get("/auth/status")
async def auth_status(
    request: Request,
    response: Response,
    authenticated: bool = Depends(optional_web_session),
    settings: Settings = Depends(get_settings),
):
    enabled = auth_enabled(settings.site_password)
    username = None
    if enabled and authenticated:
        token = request.cookies.get(COOKIE_NAME)
        data = parse_session_token(settings.session_secret, token) if token else None
        username = (data or {}).get("username") or settings.site_username
    return {
        "auth_enabled": enabled,
        "authenticated": authenticated if enabled else True,
        "idle_minutes": settings.session_idle_minutes,
        "username": username,
    }


@app.post("/auth/login")
async def auth_login(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    content_type = request.headers.get("content-type", "")
    wants_redirect = "application/json" not in content_type

    if "application/json" in content_type:
        body = await request.json()
        username = str(body.get("username", ""))
        password = str(body.get("password", ""))
    else:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

    if not auth_enabled(settings.site_password):
        if wants_redirect:
            return RedirectResponse(url="/", status_code=303)
        return {"ok": True, "auth_enabled": False}

    credentials_ok = username == settings.site_username and verify_password(
        settings.site_password, password
    )
    if not credentials_ok:
        if wants_redirect:
            return RedirectResponse(url="/login?login_error=1", status_code=303)
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    token = create_session_token(settings.session_secret, username=username)
    if wants_redirect:
        redirect = RedirectResponse(url="/", status_code=303)
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
    channel: str = "api"
    user_id: str = "test"


class ChatResponse(BaseModel):
    text: str
    agent: str
    pending_review: bool = False


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "fase_activa": settings.active_phase,
        "openai_configured": bool(settings.openai_api_key),
        "slack_configured": bool(settings.slack_bot_token),
        "whatsapp_configured": bool(settings.twilio_account_sid),
        "web_auth_enabled": auth_enabled(settings.site_password),
    }


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_web_session)])
async def chat(req: ChatRequest):
    result = await handle_message(
        InboundMessage(channel=req.channel, user_id=req.user_id, text=req.message)
    )
    return ChatResponse(**{k: result[k] for k in ("text", "agent", "pending_review") if k in result})


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
async def validation_generate_probes(req: GenerateProbesRequest):
    try:
        return await generate_probes(
            user_id=req.user_id,
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

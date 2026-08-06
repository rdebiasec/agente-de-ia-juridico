"""Allowlist de IP para escritorio/auditoría cuando no hay login.

Infraestructura (health Render, Slack, Twilio) entra por path bypass.
La IP del cliente en Render se toma de CF-Connecting-IP / True-Client-IP.
"""

from __future__ import annotations

import ipaddress
import logging
import os
from typing import Iterable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

AllowEntry = (
    ipaddress.IPv4Address
    | ipaddress.IPv6Address
    | ipaddress.IPv4Network
    | ipaddress.IPv6Network
)

_BYPASS_EXACT = frozenset({"/health"})


def parse_allowlist(raw: str) -> list[AllowEntry]:
    """Parsea CSV de IPs o CIDR (p. ej. `1.2.3.4,10.0.0.0/8`)."""
    networks: list[AllowEntry] = []
    for part in (raw or "").split(","):
        token = part.strip()
        if not token:
            continue
        try:
            if "/" in token:
                networks.append(ipaddress.ip_network(token, strict=False))
            else:
                networks.append(ipaddress.ip_address(token))
        except ValueError:
            logger.warning("IP_ALLOWLIST: entrada inválida ignorada: %r", token)
    return networks


def client_ip(request: Request) -> str:
    """IP real del cliente (Cloudflare/Render) o fallback X-Forwarded-For / socket."""
    if os.environ.get("RENDER"):
        for header in ("cf-connecting-ip", "true-client-ip"):
            value = (request.headers.get(header) or "").strip()
            if value:
                return value.split(",")[0].strip()
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if forwarded:
        return forwarded
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def path_is_bypassed(path: str) -> bool:
    if path in _BYPASS_EXACT:
        return True
    if path == "/slack" or path.startswith("/slack/"):
        return True
    if path == "/twilio" or path.startswith("/twilio/"):
        return True
    # Front-office víctima / webchat: bypass intencional del allowlist del desk.
    # Quitar sin feature-flag rompería la superficie víctima cuando IP_ALLOWLIST_ENABLED=true.
    # Leftover auditoría: documentado; no endurecer aquí sin flag + auth propia.
    if path == "/cliente" or path.startswith("/cliente/"):
        return True
    if path == "/webchat" or path.startswith("/webchat/"):
        return True
    return False


def ip_is_allowed(
    ip_str: str,
    networks: Iterable[AllowEntry],
    *,
    allow_loopback: bool,
) -> bool:
    if allow_loopback and ip_str in {"127.0.0.1", "::1", "localhost", "testclient"}:
        return True
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if allow_loopback and addr.is_loopback:
        return True
    for entry in networks:
        if isinstance(entry, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
            if addr in entry:
                return True
        elif addr == entry:
            return True
    return False


class IpAllowlistMiddleware:
    """Bloquea 403 si IP_ALLOWLIST_ENABLED y la IP no está permitida."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from src.config import get_settings

        settings = get_settings()
        if not settings.ip_allowlist_enabled:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path or "/"
        if path_is_bypassed(path):
            await self.app(scope, receive, send)
            return

        networks = parse_allowlist(settings.ip_allowlist)
        allow_loopback = not bool(os.environ.get("RENDER"))
        ip = client_ip(request)
        if ip_is_allowed(ip, networks, allow_loopback=allow_loopback):
            await self.app(scope, receive, send)
            return

        logger.warning("IP allowlist denegó path=%s ip=%s", path, ip)
        response: Response = JSONResponse(
            {
                "detail": "Acceso denegado desde esta IP.",
                "code": "ip_not_allowed",
            },
            status_code=403,
        )
        await response(scope, receive, send)

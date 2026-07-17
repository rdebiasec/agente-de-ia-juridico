"""Estado no secreto de Slack Socket Mode (observabilidad /health)."""

from __future__ import annotations

from src.config import get_settings

# Actualizado por start_slack_socket_mode al conectar Bolt.
_socket_started: bool = False


def mark_slack_socket_started(started: bool = True) -> None:
    global _socket_started
    _socket_started = started


def slack_socket_started() -> bool:
    return _socket_started


def slack_health_flags() -> dict[str, bool]:
    settings = get_settings()
    bot = bool(settings.slack_bot_token)
    signing = bool(settings.slack_signing_secret)
    app_token = bool(settings.slack_app_token)
    return {
        "slack_configured": bot and signing,
        "slack_app_token_configured": app_token,
        "slack_socket_started": _socket_started and bot and signing and app_token,
    }

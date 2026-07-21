"""Helpers de consentimiento web (Ley 1581)."""

from __future__ import annotations

from fastapi import Request

from src.compliance.policy import CURRENT_POLICY_VERSION
from src.storage import get_repository
from src.storage.models import ComplianceConsent


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "on", "yes", "si", "sí"}


def extract_consent_flags(payload: dict) -> tuple[bool, bool]:
    return _truthy(payload.get("accept_privacy")), _truthy(payload.get("accept_sensitive_data"))


def client_ip(request: Request) -> str | None:
    forwarded = (request.headers.get("x-forwarded-for") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def record_web_chat_consent(*, username: str, request: Request) -> None:
    key = f"web:{username.strip().lower()}"
    get_repository().record_compliance_consent(
        ComplianceConsent(
            subject_key=key,
            context="web_chat",
            policy_version=CURRENT_POLICY_VERSION,
            privacy_accepted=True,
            sensitive_data_ack=True,
            ip_address=client_ip(request),
            user_agent=(request.headers.get("user-agent") or "")[:500],
        )
    )

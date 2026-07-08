"""Registro de consentimiento para el chat web."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.compliance.policy import CURRENT_POLICY_VERSION, DATA_CONTROLLER
from src.storage import get_repository
from src.storage.models import ComplianceConsent

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


class WebConsentBody(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    accept_privacy: bool = False
    accept_sensitive_data: bool = False


@router.get("/policy")
async def compliance_policy():
    return {
        "version": CURRENT_POLICY_VERSION,
        "controller": DATA_CONTROLLER,
        "privacy_url": "/legal/privacidad",
        "case_data_url": "/legal/tratamiento-datos-casos",
    }


@router.post("/web-consent")
async def record_web_consent(body: WebConsentBody, request: Request):
    if not body.accept_privacy or not body.accept_sensitive_data:
        return {"ok": False, "detail": "Consentimiento incompleto."}
    ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    ua = (request.headers.get("user-agent") or "")[:500]
    key = f"web:{body.username.strip().lower()}"
    get_repository().record_compliance_consent(
        ComplianceConsent(
            subject_key=key,
            context="web_chat",
            policy_version=CURRENT_POLICY_VERSION,
            privacy_accepted=True,
            sensitive_data_ack=True,
            ip_address=ip,
            user_agent=ua,
        )
    )
    return {"ok": True, "policy_version": CURRENT_POLICY_VERSION}

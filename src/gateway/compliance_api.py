"""Registro de consentimiento, policy y ARCO para el chat web."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.auth.deps import get_session_bound_subject_id
from src.compliance.arco import erase_web_subject
from src.compliance.consent import record_web_chat_consent
from src.compliance.policy import CURRENT_POLICY_VERSION, DATA_CONTROLLER

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
        "terms_url": "/legal/terminos",
        "arco_email": DATA_CONTROLLER.get("contact_email"),
    }


@router.post("/web-consent")
async def record_web_consent(body: WebConsentBody, request: Request):
    if not body.accept_privacy or not body.accept_sensitive_data:
        return {"ok": False, "detail": "Consentimiento incompleto."}
    record_web_chat_consent(username=body.username, request=request)
    return {"ok": True, "policy_version": CURRENT_POLICY_VERSION}


@router.post("/arco-erase")
async def arco_erase_own_data(uid: str = Depends(get_session_bound_subject_id)):
    """Supresión ARCO solo del titular autenticado (cookie); ignora `?user_id=`."""
    result = erase_web_subject(uid, channel="web")
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("detail") or "No se pudo borrar.")
    return result

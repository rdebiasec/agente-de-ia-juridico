"""Esquemas de plan de ejecución e informes I/O por agente (Fase 1)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

PLAN_STATUSES = (
    "draft",
    "pending_approval",
    "approved",
    "rejected",
    "executing",
    "done",
    "failed",
)
PlanStatus = Literal[
    "draft", "pending_approval", "approved", "rejected", "executing", "done", "failed"
]
StepStatus = Literal["pending", "in_progress", "done", "blocked", "skipped"]
RiskLevel = Literal["bajo", "medio", "alto"]
ArtifactKind = Literal[
    "user_message", "expediente", "rag_chunk", "prior_step_output", "draft", "skill_output"
]
Classification = Literal["hecho", "inferencia", "pendiente_verificacion"]


class ArtifactRef(BaseModel):
    kind: ArtifactKind
    ref_id: str
    preview: str = Field(..., max_length=500)
    classification: Classification = "pendiente_verificacion"


class PlanStep(BaseModel):
    step_id: str
    order: int
    agent_id: str
    skill_id: str | None = None
    title: str
    user_summary: str
    inputs_expected: list[str] = Field(default_factory=list)
    outputs_promised: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    estimated_risk: RiskLevel = "medio"
    requires_hitl_output: bool = False
    status: StepStatus = "pending"

    @field_validator("agent_id")
    @classmethod
    def _agent_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("agent_id requerido")
        return v.strip()


class ExecutionPlan(BaseModel):
    plan_id: str
    session_id: str
    initiator_user_id: str
    channel: str = "web"
    user_message: str
    objective: str
    agents_involved: list[str] = Field(default_factory=list)
    steps: list[PlanStep] = Field(default_factory=list)
    status: PlanStatus = "pending_approval"
    created_at_ms: int
    approved_at_ms: int | None = None
    approved_by: str | None = None
    rejected_at_ms: int | None = None
    rejection_reason: str | None = None
    template_kind: str | None = None
    pattern_reused: bool = False

    def to_dict(self) -> dict:
        return self.model_dump()


class AgentIOReport(BaseModel):
    step_id: str
    agent_id: str
    received_from: str
    inputs: list[ArtifactRef] = Field(default_factory=list)
    outputs: list[ArtifactRef] = Field(default_factory=list)
    structured_output: dict | None = None
    user_update: str = ""
    status: StepStatus = "done"

    def to_dict(self) -> dict:
        return self.model_dump()


class PlanStreamEvent(BaseModel):
    """Evento SSE de ejecución de plan (Fase 2)."""

    event: str
    plan_id: str
    seq: int
    at_ms: int
    step_id: str | None = None
    payload: dict = Field(default_factory=dict)

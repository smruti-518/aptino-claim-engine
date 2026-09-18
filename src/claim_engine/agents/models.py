from typing import Literal

from pydantic import BaseModel, Field


Decision = Literal[
    "APPROVE",
    "REJECT",
    "NEEDS_REVIEW",
    "INSUFFICIENT_EVIDENCE",
]


class ClaimInput(BaseModel):
    claim_id: str
    patient_age: int | None = None
    diagnosis: str
    treatment: str
    hospital_name: str | None = None
    admission_date: str | None = None
    discharge_date: str | None = None
    claimed_amount: float | None = None
    policy_start_date: str | None = None
    notes: str | None = None


class Evidence(BaseModel):
    chunk_id: str
    page: int
    section: str
    text: str
    score: float


class AgentDecision(BaseModel):
    agent_name: str
    decision: Decision
    reasoning: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

    key_findings: list[str] = Field(default_factory=list)
    applicable_limits: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    policy_citations: list[str] = Field(default_factory=list)


class FinalDecision(BaseModel):
    claim_id: str
    decision: Decision
    reasoning: str

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    key_findings: list[str] = Field(default_factory=list)
    applicable_limits: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)

    agent_decisions: list[AgentDecision] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    policy_citations: list[str] = Field(default_factory=list)

    execution_trace: list[str] = Field(default_factory=list)

    abstention_reason: str | None = None
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SecurityEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt-{uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=utc_now)
    source_ip: str
    destination_ip: str = "10.20.0.10"
    destination_port: int | None = None
    event_type: str
    username: str | None = None
    service: str = "unknown"
    severity: str = "unknown"
    raw_message: str
    source: str = "demo"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Detection(BaseModel):
    threat_type: str
    method: Literal["rule-based", "ml"] = "rule-based"
    evidence: list[str]
    target: str


class RiskAssessment(BaseModel):
    score: int
    level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    factors: list[dict[str, Any]]


class ResponseAction(BaseModel):
    id: str = Field(default_factory=lambda: f"rsp-{uuid4().hex[:12]}")
    action: Literal["BLOCK_IP", "UNBLOCK_IP", "QUARANTINE_CONTAINER", "DISABLE_ACCOUNT", "MONITOR"]
    target: str
    reason: str
    timestamp: datetime = Field(default_factory=utc_now)
    status: Literal["executed", "simulated", "not_required"] = "simulated"
    mode: str = "simulation"


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: f"INC-{uuid4().hex[:8].upper()}")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: Literal["OPEN", "CONTAINED", "MONITORING"] = "OPEN"
    threat_type: str
    detection_method: str
    source_ip: str
    target: str
    event_ids: list[str]
    risk: RiskAssessment
    detection_evidence: list[str]
    hunting_evidence: list[str]
    timeline: list[SecurityEvent]
    response: ResponseAction | None = None
    report: dict[str, Any] | None = None


class AgentRun(BaseModel):
    id: str = Field(default_factory=lambda: f"run-{uuid4().hex[:12]}")
    agent: str
    status: str = "completed"
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime = Field(default_factory=utc_now)
    duration_ms: float = 0
    input_id: str
    output: str
    model: str | None = None
    key_identifier: str | None = None
    error_type: str | None = None

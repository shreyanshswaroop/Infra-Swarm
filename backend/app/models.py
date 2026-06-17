from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    SAFETY_REVIEW = "SAFETY_REVIEW"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"

class Severity(str, Enum):
    SEV1 = "SEV-1"
    SEV2 = "SEV-2"
    SEV3 = "SEV-3"

class AgentEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Diagnosis(BaseModel):
    root_cause: str
    confidence: float
    evidence: List[str]
    affected_services: List[str]
    recommended_action: str

class RemediationPlan(BaseModel):
    action_type: str
    target: str
    command: str
    reason: str
    risk: str
    validation: List[str]

class SafetyDecision(BaseModel):
    approved: bool
    requires_human_approval: bool
    blocked: bool
    reason: str
    blast_radius: str

class Incident(BaseModel):
    id: str = Field(default_factory=lambda: "INC-" + str(uuid.uuid4())[:8].upper())
    title: str
    severity: Severity
    status: IncidentStatus
    affected_services: List[str]
    signals: List[str]
    diagnosis: Optional[Diagnosis] = None
    remediation_plan: Optional[RemediationPlan] = None
    safety_decision: Optional[SafetyDecision] = None
    events: List[AgentEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

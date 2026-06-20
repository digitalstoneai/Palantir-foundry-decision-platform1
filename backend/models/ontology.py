from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

ObjectType = Literal["facility", "asset", "order", "incident", "team"]
StatusType = Literal["nominal", "at_risk", "degraded", "critical"]
LinkType = Literal["serves", "depends_on", "located_at", "assigned_to", "affects"]
SeverityType = Literal["urgent", "high", "normal"]


class OntologyObject(BaseModel):
    id: str
    type: ObjectType
    name: str
    status: StatusType
    owner_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class OntologyLink(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: LinkType
    weight: float = 1.0
    created_at: datetime


class Event(BaseModel):
    id: str
    object_id: str
    type: Literal["anomaly", "exception", "alert", "status_change"]
    severity: SeverityType
    description: str
    resolved: bool = False
    created_at: datetime


class ImpactAnalysisRequest(BaseModel):
    object_id: str
    event_id: Optional[str] = None


class ImpactAnalysisResponse(BaseModel):
    object_id: str
    affected_objects: list[str]
    dependency_path: list[dict]
    summary: str
    confidence: float
    ai_model: str
    degraded_mode: bool = False

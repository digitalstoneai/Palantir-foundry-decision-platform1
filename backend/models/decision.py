from typing import Optional

from pydantic import BaseModel


class DecisionOption(BaseModel):
    id: str
    event_id: str
    label: str
    description: str
    cost_impact: Optional[float] = None
    service_impact: Optional[float] = None
    risk_score: Optional[float] = None


class Constraint(BaseModel):
    name: str
    threshold: float
    weight: float


class ScenarioRequest(BaseModel):
    event_id: str
    constraints: list[Constraint]


class RecommendationResponse(BaseModel):
    recommended_option_id: str
    rationale: str
    confidence: float
    tradeoff_summary: str
    constraint_scores: dict[str, float]
    ai_model: str
    degraded_mode: bool = False


class DecisionRecordCreate(BaseModel):
    event_id: str
    option_id: str
    rationale: str
    decided_by: str


class DecisionRecord(BaseModel):
    id: str
    event_id: str
    option_id: Optional[str] = None
    rationale: Optional[str] = None
    decided_by: str
    decided_at: str
    outcome_notes: Optional[str] = None
    ai_model: Optional[str] = None

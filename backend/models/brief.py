from typing import Literal, Optional

from pydantic import BaseModel

RoleType = Literal["operations_manager", "planner", "maintenance_lead", "logistics_lead"]
ActionType = Literal["reassign", "escalate", "schedule", "notify", "defer"]
ActionStatus = Literal["pending", "approved", "rejected", "executed"]


class BriefingRequest(BaseModel):
    role: RoleType


class BriefingResponse(BaseModel):
    role: RoleType
    content: str
    top_exceptions: list[str]
    generated_at: str
    ai_model: str


class ActionRequest(BaseModel):
    type: ActionType
    object_id: str
    requested_by: str
    payload: Optional[dict] = None


class ActionApproval(BaseModel):
    action_id: str
    approved_by: str
    approved: bool


class ActionResponse(BaseModel):
    action_id: str
    status: ActionStatus
    ai_rationale: str
    ai_model: str

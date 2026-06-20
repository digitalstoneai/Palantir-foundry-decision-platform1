from typing import Optional

from fastapi import APIRouter, HTTPException

from core.config import TaskComplexity, resolve_model
from db import queries
from models.brief import ActionApproval, ActionRequest, ActionResponse, BriefingRequest, BriefingResponse
from services import ai_brief

router = APIRouter(prefix="/api/brief", tags=["missionbrief"])


@router.post("/generate", response_model=BriefingResponse)
async def generate(request: BriefingRequest):
    objects = await queries.get_objects()
    events = await queries.get_events()
    return await ai_brief.generate_briefing(role=request.role, objects=objects, events=events)


@router.post("/action", response_model=ActionResponse)
async def propose_action(request: ActionRequest):
    target = await queries.get_object(request.object_id)
    if target is None:
        raise HTTPException(status_code=404, detail=f"object '{request.object_id}' not found")

    rationale = await ai_brief.generate_action_rationale(action_type=request.type, object_data=target)
    action = await queries.create_action(
        action_type=request.type,
        object_id=request.object_id,
        requested_by=request.requested_by,
        payload=request.payload,
        ai_rationale=rationale,
    )
    return ActionResponse(
        action_id=action["id"],
        status=action["status"],
        ai_rationale=action["ai_rationale"],
        ai_model=resolve_model(TaskComplexity.FAST),
    )


@router.post("/action/{action_id}/approve", response_model=ActionResponse)
async def approve_action(action_id: str, request: ActionApproval):
    action = await queries.resolve_action(
        action_id=action_id, approved_by=request.approved_by, approved=request.approved
    )
    if action is None:
        raise HTTPException(status_code=404, detail=f"action '{action_id}' not found")
    return ActionResponse(
        action_id=action["id"],
        status=action["status"],
        ai_rationale=action["ai_rationale"],
        ai_model=resolve_model(TaskComplexity.FAST),
    )


@router.get("/actions", response_model=list[ActionResponse])
async def list_actions(status: Optional[str] = None, object_id: Optional[str] = None):
    actions = await queries.get_actions(status=status, object_id=object_id)
    model = resolve_model(TaskComplexity.FAST)
    return [
        ActionResponse(action_id=a["id"], status=a["status"], ai_rationale=a["ai_rationale"], ai_model=model)
        for a in actions
    ]

from typing import Optional

from fastapi import APIRouter, HTTPException

from db import queries
from models.decision import (
    DecisionOption,
    DecisionRecord,
    DecisionRecordCreate,
    RecommendationResponse,
    ScenarioRequest,
)
from services import ai_decision

router = APIRouter(prefix="/api/decision", tags=["decisionroom"])


@router.get("/options/{event_id}", response_model=list[DecisionOption])
async def list_options(event_id: str):
    return await queries.get_decision_options(event_id)


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: ScenarioRequest):
    event = await queries.get_event(request.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"event '{request.event_id}' not found")

    options = await queries.get_decision_options(request.event_id)
    if not options:
        raise HTTPException(status_code=404, detail=f"no decision options found for event '{request.event_id}'")

    return await ai_decision.recommend_option(event=event, options=options, constraints=request.constraints)


@router.post("/record", response_model=DecisionRecord)
async def record_decision(request: DecisionRecordCreate):
    return await queries.create_decision_record(
        event_id=request.event_id,
        option_id=request.option_id,
        rationale=request.rationale,
        decided_by=request.decided_by,
    )


@router.get("/records", response_model=list[DecisionRecord])
async def list_records(event_id: Optional[str] = None):
    return await queries.get_decision_records(event_id=event_id)

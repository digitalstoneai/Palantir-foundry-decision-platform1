from fastapi import APIRouter

from db import queries
from models.decision import DecisionOption

router = APIRouter(prefix="/api/decision", tags=["decisionroom"])


@router.get("/options/{event_id}", response_model=list[DecisionOption])
async def list_options(event_id: str):
    return await queries.get_decision_options(event_id)

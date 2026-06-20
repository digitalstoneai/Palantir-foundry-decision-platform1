from typing import Optional

from fastapi import APIRouter, HTTPException

from db import queries
from models.ontology import Event, ImpactAnalysisRequest, ImpactAnalysisResponse, OntologyLink, OntologyObject
from services import ai_opsgraph

router = APIRouter(prefix="/api/opsgraph", tags=["opsgraph"])


@router.get("/objects", response_model=list[OntologyObject])
async def list_objects():
    return await queries.get_objects()


@router.get("/objects/{object_id}", response_model=OntologyObject)
async def get_object(object_id: str):
    obj = await queries.get_object(object_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"object '{object_id}' not found")
    return obj


@router.get("/links", response_model=list[OntologyLink])
async def list_links(source_id: Optional[str] = None, target_id: Optional[str] = None):
    return await queries.get_links(source_id=source_id, target_id=target_id)


@router.get("/events", response_model=list[Event])
async def list_events(severity: Optional[str] = None, resolved: Optional[bool] = None):
    return await queries.get_events(severity=severity, resolved=resolved)


@router.post("/impact", response_model=ImpactAnalysisResponse)
async def analyze_impact(request: ImpactAnalysisRequest):
    target = await queries.get_object(request.object_id)
    if target is None:
        raise HTTPException(status_code=404, detail=f"object '{request.object_id}' not found")

    objects = await queries.get_objects()
    links = await queries.get_links()
    event = await queries.get_event(request.event_id) if request.event_id else None

    return await ai_opsgraph.analyze_impact(
        object_id=request.object_id,
        objects=objects,
        links=links,
        event=event,
    )

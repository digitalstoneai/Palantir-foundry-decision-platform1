from typing import Optional

from fastapi import APIRouter, HTTPException

from db import queries
from models.ontology import Event, OntologyLink, OntologyObject

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

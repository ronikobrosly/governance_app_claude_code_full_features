"""FastAPI router for cloud service controls."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

from src.db import get_session
from src.models.control import ControlStatus
from src.services import control_service
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/controls", tags=["controls"])


# --- Request / Response Schemas ---


class ControlCreate(BaseModel):
    name: str
    description: str
    category: str
    service_id: uuid.UUID
    owner_email: EmailStr


class ControlResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    status: ControlStatus
    category: str
    service_id: uuid.UUID
    owner_email: str

    model_config = {"from_attributes": True}


class StatusTransition(BaseModel):
    new_status: ControlStatus


# --- Endpoints ---


@router.get("/", response_model=list[ControlResponse])
async def list_controls(
    status: ControlStatus | None = Query(None),
    service_id: uuid.UUID | None = Query(None),
) -> list[ControlResponse]:
    """List controls with optional filters."""
    async with get_session() as session:
        controls = await control_service.list_controls(
            session, status=status, service_id=service_id
        )
        return [ControlResponse.model_validate(c) for c in controls]


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(control_id: uuid.UUID) -> ControlResponse:
    """Get a single control by ID."""
    try:
        async with get_session() as session:
            control = await control_service.get_control(session, control_id)
            return ControlResponse.model_validate(control)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/", response_model=ControlResponse, status_code=201)
async def create_control(body: ControlCreate) -> ControlResponse:
    """Create a new control."""
    try:
        async with get_session() as session:
            control = await control_service.create_control(
                session,
                name=body.name,
                description=body.description,
                category=body.category,
                service_id=body.service_id,
                owner_email=body.owner_email,
            )
            return ControlResponse.model_validate(control)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post("/{control_id}/transition", response_model=ControlResponse)
async def transition_status(
    control_id: uuid.UUID, body: StatusTransition
) -> ControlResponse:
    """Transition a control to a new lifecycle status."""
    try:
        async with get_session() as session:
            control = await control_service.transition_control_status(
                session, control_id, body.new_status
            )
            return ControlResponse.model_validate(control)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)

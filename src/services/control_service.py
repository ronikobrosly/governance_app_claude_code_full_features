"""Business logic for cloud service controls."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.control import CloudService, Control, ControlStatus
from src.utils.exceptions import NotFoundError, ValidationError
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def get_control(session: AsyncSession, control_id: uuid.UUID) -> Control:
    """Fetch a control by ID, raising NotFoundError if missing."""
    logger.info("fetching_control", control_id=str(control_id))
    result = await session.execute(
        select(Control)
        .options(selectinload(Control.threat_mappings))
        .where(Control.id == control_id)
    )
    control = result.scalar_one_or_none()
    if control is None:
        raise NotFoundError("Control", str(control_id))
    logger.info("control_found", control_id=str(control_id), name=control.name)
    return control


async def list_controls(
    session: AsyncSession,
    status: ControlStatus | None = None,
    service_id: uuid.UUID | None = None,
) -> list[Control]:
    """List controls with optional filters."""
    logger.info("listing_controls", status=status, service_id=str(service_id))
    query = select(Control).order_by(Control.name)
    if status is not None:
        query = query.where(Control.status == status)
    if service_id is not None:
        query = query.where(Control.service_id == service_id)
    result = await session.execute(query)
    controls = list(result.scalars().all())
    logger.info("controls_listed", count=len(controls))
    return controls


async def create_control(
    session: AsyncSession,
    name: str,
    description: str,
    category: str,
    service_id: uuid.UUID,
    owner_email: str,
) -> Control:
    """Create a new control in DRAFT status."""
    logger.info("creating_control", name=name, service_id=str(service_id))

    # Verify service exists
    svc = await session.get(CloudService, service_id)
    if svc is None:
        raise NotFoundError("CloudService", str(service_id))

    control = Control(
        name=name,
        description=description,
        category=category,
        service_id=service_id,
        owner_email=owner_email,
        status=ControlStatus.DRAFT,
    )
    session.add(control)
    await session.flush()
    logger.info("control_created", control_id=str(control.id), name=name)
    return control


async def transition_control_status(
    session: AsyncSession,
    control_id: uuid.UUID,
    new_status: ControlStatus,
) -> Control:
    """Transition a control to a new status with validation."""
    control = await get_control(session, control_id)

    valid_transitions: dict[ControlStatus, set[ControlStatus]] = {
        ControlStatus.DRAFT: {ControlStatus.ACTIVE},
        ControlStatus.ACTIVE: {ControlStatus.DEPRECATED},
        ControlStatus.DEPRECATED: {ControlStatus.ARCHIVED, ControlStatus.ACTIVE},
        ControlStatus.ARCHIVED: set(),
    }

    allowed = valid_transitions.get(control.status, set())
    if new_status not in allowed:
        raise ValidationError(
            f"Cannot transition from {control.status.value} to {new_status.value}",
            field="status",
        )

    logger.info(
        "transitioning_control",
        control_id=str(control_id),
        from_status=control.status.value,
        to_status=new_status.value,
    )
    control.status = new_status
    await session.flush()
    return control

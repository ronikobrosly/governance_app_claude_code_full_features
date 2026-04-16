"""Unit tests for control_service."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.control import Control, ControlStatus
from src.services.control_service import (
    create_control,
    get_control,
    transition_control_status,
)
from src.utils.exceptions import NotFoundError, ValidationError


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_control_not_found_raises(mock_session: AsyncMock) -> None:
    """get_control raises NotFoundError when the control doesn't exist."""
    missing_id = uuid.uuid4()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    with pytest.raises(NotFoundError) as exc_info:
        await get_control(mock_session, missing_id)

    assert str(missing_id) in exc_info.value.message


@pytest.mark.asyncio
async def test_get_control_returns_control(
    mock_session: AsyncMock, sample_control: Control
) -> None:
    """get_control returns the control when it exists."""
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sample_control
    mock_session.execute.return_value = result_mock

    result = await get_control(mock_session, sample_control.id)

    assert result.name == "Encryption at Rest"
    assert result.status == ControlStatus.ACTIVE


@pytest.mark.asyncio
async def test_create_control_validates_service_exists(
    mock_session: AsyncMock,
) -> None:
    """create_control raises NotFoundError if the service doesn't exist."""
    mock_session.get.return_value = None
    fake_service_id = uuid.uuid4()

    with pytest.raises(NotFoundError) as exc_info:
        await create_control(
            mock_session,
            name="Test Control",
            description="A test",
            category="test",
            service_id=fake_service_id,
            owner_email="test@example.com",
        )

    assert "CloudService" in exc_info.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_status,new_status,should_raise",
    [
        (ControlStatus.DRAFT, ControlStatus.ACTIVE, False),
        (ControlStatus.ACTIVE, ControlStatus.DEPRECATED, False),
        (ControlStatus.DEPRECATED, ControlStatus.ARCHIVED, False),
        (ControlStatus.DEPRECATED, ControlStatus.ACTIVE, False),
        (ControlStatus.DRAFT, ControlStatus.ARCHIVED, True),
        (ControlStatus.ACTIVE, ControlStatus.DRAFT, True),
        (ControlStatus.ARCHIVED, ControlStatus.ACTIVE, True),
    ],
)
async def test_transition_control_status_validates_transitions(
    mock_session: AsyncMock,
    sample_control: Control,
    current_status: ControlStatus,
    new_status: ControlStatus,
    should_raise: bool,
) -> None:
    """Only valid status transitions are allowed."""
    sample_control.status = current_status
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sample_control
    mock_session.execute.return_value = result_mock

    if should_raise:
        with pytest.raises(ValidationError):
            await transition_control_status(
                mock_session, sample_control.id, new_status
            )
    else:
        result = await transition_control_status(
            mock_session, sample_control.id, new_status
        )
        assert result.status == new_status

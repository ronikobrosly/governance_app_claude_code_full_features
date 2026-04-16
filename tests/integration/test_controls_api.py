"""Integration tests for the controls API endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.integration
class TestControlsAPI:
    """Tests for /api/v1/controls endpoints.

    These require a running test database.
    """

    @pytest.mark.asyncio
    async def test_health_endpoint(self) -> None:
        """The health endpoint returns ok."""
        # TODO: Set up httpx.AsyncClient with test app
        # async with AsyncClient(app=app, base_url="http://test") as client:
        #     response = await client.get("/health")
        #     assert response.status_code == 200
        #     assert response.json() == {"status": "ok"}
        pass

    @pytest.mark.asyncio
    async def test_create_and_get_control(self) -> None:
        """Creating a control and fetching it returns the same data."""
        # TODO: Implement with test DB fixtures
        pass

    @pytest.mark.asyncio
    async def test_list_controls_filters_by_status(self) -> None:
        """Listing controls with a status filter returns only matching controls."""
        # TODO: Seed multiple controls, filter, assert
        pass

    @pytest.mark.asyncio
    async def test_transition_invalid_status_returns_422(self) -> None:
        """Invalid status transitions return 422."""
        # TODO: Create DRAFT control, try to archive directly
        pass

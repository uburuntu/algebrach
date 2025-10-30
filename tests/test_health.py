"""Tests for health check endpoint."""

import pytest

from unittest.mock import AsyncMock, patch

from health import health_check


@pytest.mark.asyncio
async def test_health_check_success():
    """Test health check returns 200 when healthy."""
    mock_request = AsyncMock()

    with patch("health.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(return_value=[{"id": "rec1", "fields": {}}])

        response = await health_check(mock_request)

        assert response.status == 200
        assert "OK" in response.text
        assert "keks available" in response.text


@pytest.mark.asyncio
async def test_health_check_no_data():
    """Test health check returns 503 when no data available."""
    mock_request = AsyncMock()

    with patch("health.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(return_value=None)

        response = await health_check(mock_request)

        assert response.status == 503
        assert "ERROR" in response.text


@pytest.mark.asyncio
async def test_health_check_timeout():
    """Test health check returns 503 on timeout."""
    mock_request = AsyncMock()

    with patch("health.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(side_effect=TimeoutError())

        response = await health_check(mock_request)

        assert response.status == 503
        assert "timeout" in response.text.lower()


@pytest.mark.asyncio
async def test_health_check_unexpected_error():
    """Test health check returns 503 on unexpected error."""
    mock_request = AsyncMock()

    with patch("health.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(side_effect=Exception("Database error"))

        response = await health_check(mock_request)

        assert response.status == 503
        assert "ERROR" in response.text

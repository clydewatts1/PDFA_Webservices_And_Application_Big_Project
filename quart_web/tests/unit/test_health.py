"""Unit tests for landing health route behavior (US1)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from quart_web.src.clients.errors import MCPConnectionError


@pytest.mark.asyncio
async def test_landing_health_success_enables_login_ui(app):
    """GET / calls get_system_health and renders healthy/login-enabled state."""
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "health_status": "CONNECTED",
        "health_status_description": "Database connection is healthy",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.get("/")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "MCP Healthy" in body
    assert "Backend connection is healthy" in body
    assert "disabled" not in body
    mock_mcp.call_tool.assert_awaited_once_with("get_system_health", {})


@pytest.mark.asyncio
async def test_landing_health_failure_disables_login_ui(app):
    """GET / renders backend-unavailable fallback when health tool call fails."""
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.side_effect = MCPConnectionError("MCP unavailable")
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.get("/")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "MCP Unavailable" in body
    assert "The backend is currently unavailable" in body
    assert "disabled" in body
    mock_mcp.call_tool.assert_awaited_once_with("get_system_health", {})


@pytest.mark.asyncio
async def test_landing_template_shows_healthy_badge_when_connected(app):
    """Template contains healthy-state badge text when MCP health succeeds."""
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "health_status": "CONNECTED",
        "health_status_description": "OK",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.get("/")
    body = (await response.get_data()).decode()

    assert "badge bg-success" in body
    assert "MCP Healthy" in body


@pytest.mark.asyncio
async def test_landing_template_shows_unhealthy_badge_when_disconnected(app):
    """Template contains unhealthy-state badge and disabled controls on failure."""
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.side_effect = RuntimeError("connection dropped")
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.get("/")
    body = (await response.get_data()).decode()

    assert "badge bg-danger" in body
    assert "MCP Unavailable" in body
    assert "Login (disabled)" in body

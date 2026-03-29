"""Unit tests for MCP client payload normalization."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from quart_web.src.clients.errors import MCPToolError
from quart_web.src.clients.mcp_client import MCPClientWrapper


@pytest.mark.asyncio
async def test_call_tool_uses_structured_content_when_available():
    wrapper = MCPClientWrapper(url="http://127.0.0.1:5001/sse")
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = SimpleNamespace(
        structuredContent={"status": "SUCCESS", "health_status": "CONNECTED"},
        content=[],
    )
    wrapper._session = mock_session

    result = await wrapper.call_tool("get_system_health", {})

    assert result["status"] == "SUCCESS"
    assert result["health_status"] == "CONNECTED"


@pytest.mark.asyncio
async def test_call_tool_parses_json_text_payload():
    wrapper = MCPClientWrapper(url="http://127.0.0.1:5001/sse")
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = SimpleNamespace(
        content=[SimpleNamespace(text='{"status":"SUCCESS","health_status":"CONNECTED"}')],
    )
    wrapper._session = mock_session

    result = await wrapper.call_tool("get_system_health", {})

    assert result["status"] == "SUCCESS"
    assert result["health_status"] == "CONNECTED"


@pytest.mark.asyncio
async def test_call_tool_parses_python_dict_text_payload():
    wrapper = MCPClientWrapper(url="http://127.0.0.1:5001/sse")
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = SimpleNamespace(
        content=[SimpleNamespace(text="{'status': 'SUCCESS', 'health_status': 'CONNECTED'}")],
    )
    wrapper._session = mock_session

    result = await wrapper.call_tool("get_system_health", {})

    assert result["status"] == "SUCCESS"
    assert result["health_status"] == "CONNECTED"


@pytest.mark.asyncio
async def test_call_tool_raises_when_text_payload_is_not_parseable():
    wrapper = MCPClientWrapper(url="http://127.0.0.1:5001/sse")
    mock_session = AsyncMock()
    mock_session.call_tool.return_value = SimpleNamespace(
        content=[SimpleNamespace(text="NOT JSON")],
    )
    wrapper._session = mock_session

    with pytest.raises(MCPToolError, match="invalid JSON text content"):
        await wrapper.call_tool("get_system_health", {})

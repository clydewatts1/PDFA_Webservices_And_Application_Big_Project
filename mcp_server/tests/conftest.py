"""Shared FastMCP runtime test harness helpers."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from mcp_server.src.api.app import create_runtime_app


@pytest.fixture
def runtime_server():
    """Build the shared FastMCP runtime used by transport-aware tests."""

    return create_runtime_app()


@pytest.fixture
def runtime_tool_names(runtime_server) -> list[str]:
    """Return the registered canonical tool names for discovery assertions."""

    return sorted(tool.name for tool in runtime_server.list_tools())


@pytest.fixture
def network_runtime_settings(runtime_server) -> Iterator[tuple[str, int]]:
    """Expose the network runtime bind settings for SSE/HTTP smoke tests."""

    yield runtime_server.settings.host, runtime_server.settings.port


def normalize_tool_result(payload: dict) -> dict:
    """Strip transport metadata and keep only business result contract fields."""

    return {
        "status": payload.get("status"),
        "status_message": payload.get("status_message"),
        "data": payload.get("data"),
    }

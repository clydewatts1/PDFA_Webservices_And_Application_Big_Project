"""Shared Flask web-tier test helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class FakeMCPClient:
    """Programmable fake MCP client for Flask unit and integration tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._responses: dict[str, Any] = {}

    def set_response(self, method: str, value: Any) -> None:
        self._responses[method] = value

    def call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((method, params))
        response = self._responses.get(method, {"status": "SUCCESS"})
        if isinstance(response, Exception):
            raise response
        if isinstance(response, Callable):
            resolved = response(params)
            return resolved if isinstance(resolved, dict) else {"value": resolved}
        return response if isinstance(response, dict) else {"value": response}
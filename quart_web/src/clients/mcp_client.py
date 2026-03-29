"""Async MCP SSE client wrapper used by Quart routes."""

from __future__ import annotations

import ast
import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

from quart_web.src.clients.errors import (
    MCPConfigurationError,
    MCPConnectionError,
    MCPTimeoutError,
    MCPToolError,
)


class MCPClientWrapper:
    """Lazily connected MCP SSE client with a single session per app instance."""

    def __init__(self, *, url: str, timeout_seconds: float = 10.0) -> None:
        if not url:
            raise MCPConfigurationError("MCP_SERVER_URL is required")
        self._url = url
        self._timeout_seconds = float(timeout_seconds)
        self._session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None
        self._connect_lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self._session is not None

    async def connect(self) -> None:
        """Open SSE stream and initialize an MCP session if not yet connected."""
        if self._session is not None:
            return

        async with self._connect_lock:
            if self._session is not None:
                return

            stack = AsyncExitStack()
            try:
                read, write = await stack.enter_async_context(sse_client(url=self._url))
                session = await stack.enter_async_context(ClientSession(read, write))
                await asyncio.wait_for(session.initialize(), timeout=self._timeout_seconds)
            except asyncio.TimeoutError as exc:
                await stack.aclose()
                raise MCPTimeoutError(
                    f"Timed out while initializing MCP session after {self._timeout_seconds:.1f}s"
                ) from exc
            except Exception as exc:
                await stack.aclose()
                raise MCPConnectionError(f"Failed to connect to MCP SSE endpoint: {exc}") from exc

            self._stack = stack
            self._session = session

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call an MCP tool with timeout and normalize payload content into a dict."""
        if not tool_name:
            raise MCPToolError("tool_name is required")

        if self._session is None:
            await self.connect()

        assert self._session is not None
        payload = arguments or {}

        try:
            result = await asyncio.wait_for(
                self._session.call_tool(tool_name, arguments=payload),
                timeout=self._timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise MCPTimeoutError(
                f"Tool '{tool_name}' timed out after {self._timeout_seconds:.1f}s"
            ) from exc
        except (ConnectionError, OSError) as exc:
            raise MCPConnectionError(f"Connection dropped during '{tool_name}': {exc}") from exc
        except Exception as exc:
            raise MCPToolError(f"Tool '{tool_name}' failed: {exc}") from exc

        structured_payload = getattr(result, "structuredContent", None)
        if structured_payload is None:
            structured_payload = getattr(result, "structured_content", None)
        if structured_payload is not None:
            return self._coerce_payload_to_dict(structured_payload, tool_name)

        content_items = getattr(result, "content", None)
        if not content_items:
            raise MCPToolError(f"Tool '{tool_name}' returned no content")

        text_payload = None
        for item in content_items:
            text_value = getattr(item, "text", None)
            if text_value:
                text_payload = text_value
                break

        if text_payload is None:
            raise MCPToolError(f"Tool '{tool_name}' returned non-text content")

        return self._coerce_payload_to_dict(text_payload, tool_name)

    @staticmethod
    def _coerce_payload_to_dict(payload: Any, tool_name: str) -> dict[str, Any]:
        """Convert MCP payload objects or text into the dict contract expected by routes."""

        if isinstance(payload, dict):
            return payload

        if hasattr(payload, "items"):
            return dict(payload)

        if not isinstance(payload, str):
            raise MCPToolError(
                f"Tool '{tool_name}' returned unsupported payload type: {type(payload).__name__}"
            )

        text_payload = payload.strip()
        if not text_payload:
            raise MCPToolError(f"Tool '{tool_name}' returned empty text payload")

        try:
            parsed = json.loads(text_payload)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(text_payload)
            except (SyntaxError, ValueError) as exc:
                raise MCPToolError(f"Tool '{tool_name}' returned invalid JSON text content") from exc

        if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
            return parsed[0]
        if not isinstance(parsed, dict):
            raise MCPToolError(f"Tool '{tool_name}' returned payload that is not an object")
        return parsed

    async def close(self) -> None:
        """Close active MCP transport/session resources."""
        if self._stack is not None:
            await self._stack.aclose()
        self._stack = None
        self._session = None

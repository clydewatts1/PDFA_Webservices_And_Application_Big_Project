"""Web-tier MCP client exceptions."""

from __future__ import annotations


class MCPClientError(RuntimeError):
    """Base class for MCP client failures in the Quart tier."""

    status_code = 502

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MCPTimeoutError(MCPClientError):
    """Raised when an MCP call exceeds the configured timeout."""

    status_code = 504


class MCPConnectionError(MCPClientError):
    """Raised when SSE connection/initialization fails or drops."""

    status_code = 503


class MCPToolError(MCPClientError):
    """Raised when MCP tool invocation payload/shape is invalid."""

    status_code = 502


class MCPConfigurationError(MCPClientError):
    """Raised when required web-tier configuration is missing/invalid."""

    status_code = 500

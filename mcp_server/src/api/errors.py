"""Shared RPC-facing error types for MCP handler adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class JsonRpcError(Exception):
    """Structured RPC error payload container used by transport adapters."""

    code: int
    message: str
    data: dict[str, Any] | None = None

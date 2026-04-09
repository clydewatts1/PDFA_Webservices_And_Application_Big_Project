"""Synchronous HTTP JSON-RPC client used by the Flask web tier."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urlparse

import requests


logger = logging.getLogger("pdfa.flask.mcp_client")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class MCPClientError(RuntimeError):
    """Raised when the MCP wrapper returns a transport or JSON-RPC error."""

    def __init__(
        self,
        *,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
        status_code: int = 502,
    ) -> None:
        self.code = code
        self.message = message
        self.data = data or {}
        self.status_code = status_code
        super().__init__(f"[{code}] {message}: {self.data}")


def normalize_rpc_url(url: str) -> str:
    """Normalize configured MCP URLs to the canonical /rpc endpoint."""

    candidate = url.strip().rstrip("/")
    if not candidate:
        return "http://127.0.0.1:5001/rpc"

    parsed = urlparse(candidate)
    if parsed.path in {"", "/"}:
        return f"{candidate}/rpc"
    if parsed.path.endswith("/rpc"):
        return candidate
    return candidate


class MCPClient:
    """Thin JSON-RPC client wrapper with structured transport normalization."""

    def __init__(self, rpc_url: str, timeout_seconds: int = 30) -> None:
        self.rpc_url = normalize_rpc_url(rpc_url)
        self.timeout_seconds = timeout_seconds

    def call(self, method: str, params: dict[str, Any], request_id: str | int = 1) -> dict[str, Any]:
        """Call an MCP JSON-RPC method and return the result payload."""

        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                headers={"Accept": "application/json"},
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise MCPClientError(
                code=502,
                message="Unable to reach MCP RPC endpoint",
                data={"reason": str(exc), "rpc_url": self.rpc_url},
                status_code=502,
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise MCPClientError(
                code=response.status_code or 502,
                message="MCP RPC endpoint returned invalid JSON",
                data={"rpc_url": self.rpc_url, "status_code": response.status_code},
                status_code=response.status_code or 502,
            ) from exc

        logger.info(
            json.dumps(
                {
                    "event": "flask.mcp.call.completed",
                    "method": method,
                    "request_id": request_id,
                    "status_code": response.status_code,
                }
            )
        )

        if response.status_code >= 400:
            error_payload = data.get("error") if isinstance(data, dict) else None
            raise MCPClientError(
                code=int((error_payload or {}).get("code", response.status_code or 502)),
                message=str((error_payload or {}).get("message", "MCP transport error")),
                data=(error_payload or {}).get("data") or {"rpc_url": self.rpc_url},
                status_code=response.status_code or 502,
            )

        if not isinstance(data, dict):
            raise MCPClientError(
                code=502,
                message="MCP RPC endpoint returned an unsupported payload shape",
                data={"rpc_url": self.rpc_url},
                status_code=502,
            )

        if "error" in data:
            err = data["error"]
            raise MCPClientError(
                code=int(err.get("code", 5000)),
                message=str(err.get("message", "unknown_error")),
                data=err.get("data") or {},
                status_code=response.status_code or 200,
            )

        result = data.get("result", {})
        if isinstance(result, dict):
            return result
        if result is None:
            return {}
        return {"value": result}

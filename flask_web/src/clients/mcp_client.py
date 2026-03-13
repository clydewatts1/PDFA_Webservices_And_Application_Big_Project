from __future__ import annotations

import json
import logging
from typing import Any

import requests


logger = logging.getLogger("pdfa.flask.mcp_client")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class MCPClientError(RuntimeError):
    def __init__(self, *, code: int, message: str, data: dict[str, Any] | None = None) -> None:
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"[{code}] {message}: {self.data}")


class MCPClient:
    def __init__(self, base_url: str, timeout_seconds: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def call(self, method: str, params: dict[str, Any], request_id: str | int = 1) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        response = requests.post(
            f"{self.base_url}/rpc",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()

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

        if "error" in data:
            err = data["error"]
            raise MCPClientError(
                code=int(err.get("code", 5000)),
                message=str(err.get("message", "unknown_error")),
                data=err.get("data") or {},
            )
        return data.get("result", {})

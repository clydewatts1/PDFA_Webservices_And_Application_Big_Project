"""Canonical Flask WSGI wrapper for synchronous MCP JSON-RPC access."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

from dotenv import load_dotenv
from flask import Flask, jsonify

from mcp_server.src.api.app import create_app as create_transport_app
from mcp_server.src.db.session import make_session_factory
from mcp_server.src.lib.mcp_config import ConfigError, get_mock_user_map, load_mcp_config
from mcp_server.src.lib.tool_adapter import build_runtime_tool_adapter
from mcp_server.src.services.validation import ValidationError, validate_mcp_config, validate_transport_compatibility


logger = logging.getLogger("pdfa.mcp.wsgi")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def create_handler_map(config_path: str | None = None) -> dict[str, Handler]:
    """Build the canonical handler map used by the WSGI wrapper."""

    load_dotenv()
    config = load_mcp_config(config_path)
    validate_mcp_config(config)
    validate_transport_compatibility(config)
    mock_users = get_mock_user_map(config)
    return build_runtime_tool_adapter(make_session_factory(), mock_users)


def create_app(
    *,
    config_path: str | None = None,
    handler_map: dict[str, Handler] | None = None,
) -> Flask:
    """Create the canonical WSGI wrapper application."""

    app = create_transport_app()
    handlers = handler_map or create_handler_map(config_path=config_path)
    for method, handler in handlers.items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]

    @app.get("/health")
    def health() -> tuple[Any, int]:
        """Expose a lightweight readiness endpoint for deployment checks."""

        payload = {
            "status": "ok",
            "transport": "http-jsonrpc",
            "rpc_path": "/rpc",
            "registered_method_count": len(handlers),
        }
        logger.info(json.dumps({"event": "mcp.wrapper.health", **payload}))
        return jsonify(payload), 200

    return app


def main() -> int:
    """Launch the canonical WSGI wrapper with environment-driven bind settings."""

    try:
        app = create_app(config_path=os.getenv("MCP_CONFIG_PATH"))
    except (ConfigError, ValidationError, KeyError) as exc:
        logger.error(json.dumps({"event": "mcp.wrapper.startup.failed", "reason": str(exc)}))
        return 1

    host = os.getenv("MCP_WRAPPER_HOST") or os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_WRAPPER_PORT") or os.getenv("MCP_PORT", "5001"))
    app.run(host=host, port=port, debug=False)
    return 0


app = create_app(config_path=os.getenv("MCP_CONFIG_PATH"))


if __name__ == "__main__":
    raise SystemExit(main())
"""MCP JSON-RPC application bootstrap and transport envelope handlers."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
import time
from typing import Any, Callable

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from mcp_server.src.db.session import make_session_factory
from mcp_server.src.lib.mcp_config import ConfigError, get_mock_user_map, load_mcp_config
from mcp_server.src.services.validation import ValidationError, validate_mcp_config


logger = logging.getLogger("pdfa.mcp")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


@dataclass
class JsonRpcError(Exception):
    """Structured JSON-RPC error payload container."""

    code: int
    message: str
    data: dict[str, Any] | None = None


Handler = Callable[[dict[str, Any]], dict[str, Any]]


def create_app() -> Flask:
    """Create and configure the MCP Flask application."""

    app = Flask(__name__)
    handlers: dict[str, Handler] = {}

    def register(method: str, handler: Handler) -> None:
        """Register a JSON-RPC method handler."""

        handlers[method] = handler

    def _response(result: dict[str, Any], request_id: str | int | None) -> tuple[Any, int]:
        """Build a JSON-RPC success envelope."""

        return jsonify({"jsonrpc": "2.0", "id": request_id, "result": result}), 200

    def _error(error: JsonRpcError, request_id: str | int | None) -> tuple[Any, int]:
        """Build a JSON-RPC error envelope."""

        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "data": error.data or {},
                    },
                }
            ),
            200,
        )

    @app.post("/rpc")
    def rpc() -> tuple[Any, int]:
        """Execute one JSON-RPC request against registered handlers."""

        started_at = time.perf_counter()
        payload = request.get_json(silent=True) or {}
        request_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params") or {}

        logger.info(
            json.dumps(
                {
                    "event": "mcp.request.received",
                    "method": method,
                    "request_id": request_id,
                    "params_keys": sorted(params.keys()) if isinstance(params, dict) else [],
                }
            )
        )

        if payload.get("jsonrpc") != "2.0":
            logger.warning(json.dumps({"event": "mcp.request.invalid_version", "request_id": request_id}))
            return _error(JsonRpcError(code=4000, message="Invalid JSON-RPC version"), request_id)
        if not isinstance(method, str):
            logger.warning(json.dumps({"event": "mcp.request.invalid_method_type", "request_id": request_id}))
            return _error(JsonRpcError(code=4001, message="Method must be a string"), request_id)
        if method not in handlers:
            logger.warning(
                json.dumps(
                    {"event": "mcp.request.method_not_found", "request_id": request_id, "method": method}
                )
            )
            return _error(JsonRpcError(code=4004, message="Method not found", data={"method": method}), request_id)

        try:
            result = handlers[method](params)
            logger.info(
                json.dumps(
                    {
                        "event": "mcp.request.succeeded",
                        "method": method,
                        "request_id": request_id,
                        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                    }
                )
            )
            return _response(result, request_id)
        except JsonRpcError as error:
            logger.warning(
                json.dumps(
                    {
                        "event": "mcp.request.failed",
                        "method": method,
                        "request_id": request_id,
                        "error_code": error.code,
                        "error_message": error.message,
                        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                    }
                )
            )
            return _error(error, request_id)
        except Exception as error:  # pragma: no cover
            logger.exception(
                json.dumps(
                    {
                        "event": "mcp.request.exception",
                        "method": method,
                        "request_id": request_id,
                        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                    }
                )
            )
            return _error(
                JsonRpcError(code=5000, message="Internal error", data={"reason": str(error)}),
                request_id,
            )

    app.register_jsonrpc_handler = register  # type: ignore[attr-defined]
    return app


def register_runtime_handlers(app: Flask, mock_users: dict[str, str]) -> None:
    """Register workflow/dependent/instance/system handlers for runtime app."""

    from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers
    from mcp_server.src.api.handlers.instance_handlers import make_instance_handlers
    from mcp_server.src.api.handlers.system_handlers import make_system_handlers
    from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers

    session_factory = make_session_factory()
    for method, handler in make_workflow_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]
    for method, handler in make_all_dependent_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]
    for method, handler in make_instance_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]
    for method, handler in make_system_handlers(session_factory, mock_users).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]


def create_runtime_app(config_path: str | None = None) -> Flask:
    """Build a production runtime app with config and default handlers loaded."""

    load_dotenv()
    config = load_mcp_config(config_path)
    validate_mcp_config(config)
    mock_users = get_mock_user_map(config)

    app = create_app()
    register_runtime_handlers(app, mock_users)
    return app


app = create_app()


if __name__ == "__main__":
    try:
        runtime_app = create_runtime_app()
    except (ConfigError, ValidationError, KeyError) as exc:
        logger.error(json.dumps({"event": "mcp.startup.failed", "reason": str(exc)}))
        raise SystemExit(1) from exc

    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "5001"))
    runtime_app.run(host=host, port=port, debug=False)

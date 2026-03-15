"""Dedicated MCP stdio entrypoint for Inspector compatibility."""

from __future__ import annotations

import inspect
import os
import sys
from typing import Any, Optional

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from mcp_server.src.db.session import make_session_factory
from mcp_server.src.lib.mcp_config import ConfigError, get_mock_user_map, load_mcp_config
from mcp_server.src.lib.tool_adapter import build_runtime_tool_adapter
from mcp_server.src.services.auth_service import reset_auth_sessions
from mcp_server.src.services.validation import ValidationError, validate_mcp_config, validate_transport_compatibility

TYPE_MAP = {"string": str, "integer": int, "boolean": bool}


def _make_typed_tool(
    mcp_server: Any,
    method_name: str,
    method_handler: Any,
    tool_def: dict,
) -> None:
    """Register a tool on the FastMCP server with a typed signature from the YAML tool definition."""
    params_meta = tool_def.get("parameters") or {}
    description = str(tool_def.get("description", ""))

    sig_params = []
    annotations: dict[str, Any] = {}
    required_params: list[tuple[str, Any]] = []
    optional_params: list[tuple[str, Any]] = []

    for param_name, meta in params_meta.items():
        if isinstance(meta, dict):
            py_type = TYPE_MAP.get(meta.get("type", "string"), str)
            required = meta.get("required", True)
        else:
            py_type = str
            required = True

        if required:
            required_params.append((param_name, py_type))
        else:
            optional_params.append((param_name, py_type))

    for param_name, py_type in required_params:
        sig_params.append(inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=py_type,
        ))
        annotations[param_name] = py_type

    for param_name, py_type in optional_params:
        sig_params.append(inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Optional[py_type],
            default=None,
        ))
        annotations[param_name] = Optional[py_type]

    def _tool_fn(**kwargs: Any) -> dict[str, Any]:
        return method_handler(kwargs)

    _tool_fn.__name__ = method_name
    _tool_fn.__doc__ = description or None
    _tool_fn.__annotations__ = annotations
    if sig_params:
        _tool_fn.__signature__ = inspect.Signature(sig_params)

    mcp_server.tool(name=method_name, description=description)(_tool_fn)


def create_stdio_server(config_path: str | None = None) -> Any:
    """Build a FastMCP stdio server and register canonical dotted tools."""

    load_dotenv()
    config = load_mcp_config(config_path)
    validate_mcp_config(config)
    validate_transport_compatibility(config)
    reset_auth_sessions()

    mock_users = get_mock_user_map(config)
    handlers = build_runtime_tool_adapter(make_session_factory(), mock_users)

    server_name = str(config.get("server_name", "WB-Workflow-Configuration"))
    mcp = FastMCP(server_name)

    # Supports both new dict format {name, description, parameters} and old plain-string list
    tool_defs: dict[str, dict] = {}
    for t in config.get("tools", []):
        if isinstance(t, dict) and "name" in t:
            tool_defs[t["name"]] = t

    for method_name, method_handler in handlers.items():
        tool_def = tool_defs.get(method_name, {})
        _make_typed_tool(mcp, method_name, method_handler, tool_def)

    return mcp


def main() -> int:
    """Launch MCP stdio transport with canonical command semantics."""

    config_path = os.getenv("MCP_CONFIG_PATH")
    try:
        mcp = create_stdio_server(config_path=config_path)
        mcp.run(transport="stdio")
        return 0
    except (ConfigError, ValidationError, KeyError) as exc:
        print(f"MCP stdio startup failed: {exc}", file=sys.stderr)  # stderr, NOT stdout
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

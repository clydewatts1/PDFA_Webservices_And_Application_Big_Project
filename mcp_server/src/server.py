"""Dedicated MCP stdio entrypoint for Inspector compatibility."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from mcp_server.src.db.session import make_session_factory
from mcp_server.src.lib.mcp_config import ConfigError, get_mock_user_map, load_mcp_config
from mcp_server.src.lib.tool_adapter import build_runtime_tool_adapter
from mcp_server.src.services.validation import ValidationError, validate_mcp_config, validate_transport_compatibility


def _load_fastmcp() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise SystemExit("The MCP SDK is required. Install dependencies from requirements.txt.") from exc
    return FastMCP


def create_stdio_server(config_path: str | None = None) -> Any:
    """Build a FastMCP stdio server and register canonical dotted tools."""

    load_dotenv()
    config = load_mcp_config(config_path)
    validate_mcp_config(config)
    validate_transport_compatibility(config)

    mock_users = get_mock_user_map(config)
    handlers = build_runtime_tool_adapter(make_session_factory(), mock_users)

    FastMCP = _load_fastmcp()
    server_name = str(config.get("server_name", "WB-Workflow-Configuration"))
    mcp = FastMCP(server_name)

    for method, handler in handlers.items():
        def _make_tool(method_name: str, method_handler: Any) -> None:
            @mcp.tool(name=method_name)
            def _dynamic_tool(**kwargs: Any) -> dict[str, Any]:
                params = dict(kwargs)
                return method_handler(params)

        _make_tool(method, handler)

    return mcp


def main() -> int:
    """Launch MCP stdio transport with canonical command semantics."""

    config_path = os.getenv("MCP_CONFIG_PATH")
    try:
        mcp = create_stdio_server(config_path=config_path)
        mcp.run(transport="stdio")
        return 0
    except (ConfigError, ValidationError, KeyError) as exc:
        print(f"MCP stdio startup failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

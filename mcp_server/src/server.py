"""Dedicated MCP runtime entrypoint for stdio, SSE, and streamable-http."""

from __future__ import annotations

import inspect
import os
import sys
from typing import Any, Optional

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from mcp_server.src.api.app import create_runtime_app
from mcp_server.src.lib.mcp_config import ConfigError
from mcp_server.src.lib.runtime_profile import RuntimeProfileError, build_runtime_arg_parser, build_runtime_profile
from mcp_server.src.services.validation import ValidationError


def _run_network_runtime(app: Any, *, transport: str, host: str, port: int) -> None:
    """Run the current network runtime with compatibility for Flask and FastMCP apps."""

    if hasattr(app, "settings"):
        app.settings.host = host
        app.settings.port = port
        app.run(transport=transport)
        return

    if hasattr(app, "run"):
        app.run(host=host, port=port, debug=False)
        return

    raise TypeError("Runtime application does not expose a compatible run() method")


def main() -> int:
    """Launch MCP stdio transport with canonical command semantics."""
    parser = build_runtime_arg_parser()
    args = parser.parse_args()
    try:
        profile = build_runtime_profile(args, os.environ)
    except RuntimeProfileError as exc:
        print(f"MCP startup argument validation failed: {exc}", file=sys.stderr)
        return 1

    config_path = profile.config_path
    if profile.transport == "stdio":
        try:
            mcp = create_runtime_app(config_path=config_path)
            mcp.run(transport="stdio")
            return 0
        except (ConfigError, ValidationError, KeyError) as exc:
            print(f"MCP stdio startup failed: {exc}", file=sys.stderr)  # stderr, NOT stdout
            return 1
    elif profile.transport == "sse":
        try:
            app = create_runtime_app(config_path=config_path)
            _run_network_runtime(app, transport="sse", host=profile.host, port=profile.port)
            return 0
        except (ConfigError, ValidationError, KeyError) as exc:
            print(f"MCP SSE startup failed: {exc}", file=sys.stderr)  # stderr, NOT stdout
            return 1
    elif profile.transport == "streamable-http":
        try:
            app = create_runtime_app(config_path=config_path)
            _run_network_runtime(app, transport="streamable-http", host=profile.host, port=profile.port)
            return 0
        except (ConfigError, ValidationError, KeyError) as exc:
            print(f"MCP HTTP startup failed: {exc}", file=sys.stderr)  # stderr, NOT stdout
            return 1
    else:
        print(f"Unknown transport: {profile.transport}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

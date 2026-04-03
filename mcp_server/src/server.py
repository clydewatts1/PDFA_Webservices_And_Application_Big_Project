"""Dedicated MCP runtime entrypoint for stdio, SSE, and streamable-http."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime, timedelta
from typing import Any

from mcp_server.src.api.app import create_runtime_app
from mcp_server.src.lib.mcp_config import ConfigError
from mcp_server.src.lib.runtime_profile import RuntimeProfileError, build_runtime_arg_parser, build_runtime_profile
from mcp_server.src.services.system_service import get_runtime_db_url_error
from mcp_server.src.services.validation import ValidationError


logger = logging.getLogger("pdfa.mcp.startup")


def _parse_cutover_window(environ: dict[str, str]) -> dict[str, str] | None:
    raw_start = (environ.get("CUTOVER_WINDOW_START_UTC") or "").strip()
    if not raw_start:
        return None

    normalized_start = raw_start.replace("Z", "+00:00")
    started_at = datetime.fromisoformat(normalized_start)
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    started_at = started_at.astimezone(UTC)

    rollback_window_hours = int((environ.get("ROLLBACK_WINDOW_HOURS") or "24").strip())
    if rollback_window_hours < 1:
        raise ValueError("ROLLBACK_WINDOW_HOURS must be greater than zero")

    deadline = started_at + timedelta(hours=rollback_window_hours)
    decision_owner = (environ.get("CUTOVER_DECISION_OWNER") or "unassigned").strip() or "unassigned"
    return {
        "cutover_start_utc": started_at.isoformat().replace("+00:00", "Z"),
        "rollback_deadline_utc": deadline.isoformat().replace("+00:00", "Z"),
        "rollback_window_hours": str(rollback_window_hours),
        "decision_owner": decision_owner,
    }


def _log_cutover_window(environ: dict[str, str]) -> None:
    cutover_window = _parse_cutover_window(environ)
    if cutover_window is None:
        logger.info(json.dumps({"event": "mcp.cutover.window.not_configured", "rollback_window_hours": 24}))
        return

    logger.info(json.dumps({"event": "mcp.cutover.window.started", **cutover_window}))


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

    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    parser = build_runtime_arg_parser()
    args = parser.parse_args()
    try:
        profile = build_runtime_profile(args, os.environ)
    except RuntimeProfileError as exc:
        print(f"MCP startup argument validation failed: {exc}", file=sys.stderr)
        return 1

    db_url_error = get_runtime_db_url_error()
    if db_url_error is not None and db_url_error.get("health_status_error") in {
        "legacy_postgresql_runtime",
        "unsupported_db_scheme",
    }:
        print(f"MCP startup configuration failed: {db_url_error['health_status_error_detail']}", file=sys.stderr)
        return 1

    try:
        _log_cutover_window(dict(os.environ))
    except ValueError as exc:
        print(f"MCP startup configuration failed: {exc}", file=sys.stderr)
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

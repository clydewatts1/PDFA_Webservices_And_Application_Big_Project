"""System-level service helpers for MCP operational checks."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from mcp_server.src.lib.tool_result import success_result


def get_system_health(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    """Return database connectivity health for MCP runtime."""

    try:
        with session_factory() as session:
            session.execute(text("SELECT 1"))
        return success_result(
            status_message="Health check completed",
            payload={
                "health_status": "CONNECTED",
                "health_status_description": "Database connection is healthy",
                "health_status_error": "",
                "health_status_error_detail": "",
            },
        )
    except Exception as exc:
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "FAILED",
            "health_status_description": "Database connectivity check failed",
            "health_status_error": "db_connection_failed",
            "health_status_error_detail": str(exc),
        }

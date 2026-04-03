"""System-level service helpers for MCP operational checks."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from mcp_server.src.lib.tool_result import success_result


MYSQL_EXAMPLE_URL = "mysql+pymysql://user:password@127.0.0.1:3306/pdfa_workflow?charset=utf8mb4"


def _runtime_db_url() -> str:
    return (os.getenv("DB_URL") or "").strip()


def get_runtime_db_url_error(db_url: str | None = None) -> dict[str, Any] | None:
    """Return a structured startup/health error when DB_URL is missing or unsupported."""

    url = (db_url or _runtime_db_url()).strip()
    if not url:
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "DEAD",
            "health_status_description": "Database configuration missing",
            "health_status_error": "db_url_missing",
            "health_status_error_detail": "DB_URL environment variable is not set",
        }

    scheme = urlsplit(url).scheme.lower()
    if scheme.startswith("postgres"):
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "FAILED",
            "health_status_description": "Legacy PostgreSQL runtime is not allowed for MySQL cutover validation",
            "health_status_error": "legacy_postgresql_runtime",
            "health_status_error_detail": (
                "DB_URL points to PostgreSQL. Set DB_URL to a MySQL URL before cutover validation, for example "
                f"{MYSQL_EXAMPLE_URL}"
            ),
        }

    if not scheme.startswith("mysql") and not scheme.startswith("sqlite"):
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "FAILED",
            "health_status_description": "Database URL scheme is unsupported",
            "health_status_error": "unsupported_db_scheme",
            "health_status_error_detail": (
                f"DB_URL must use a MySQL URL for sign-off validation. Example: {MYSQL_EXAMPLE_URL}"
            ),
        }

    return None


def get_system_health(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    """Return database connectivity health for MCP runtime."""

    db_url_error = get_runtime_db_url_error()
    if db_url_error is not None:
        return db_url_error

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
    except OperationalError as exc:
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "DISCONNECTED",
            "health_status_description": "Database is unreachable",
            "health_status_error": "db_connection_failed",
            "health_status_error_detail": str(exc),
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "status_message": "Health check failed",
            "health_status": "FAILED",
            "health_status_description": "Database connectivity check failed",
            "health_status_error": "db_connection_failed",
            "health_status_error_detail": str(exc),
        }

"""Health routes for the canonical Flask web tier."""

from __future__ import annotations

import json
import logging
import time

from flask import Blueprint, current_app, render_template, session

from flask_web.src.clients.mcp_client import MCPClientError


health_bp = Blueprint("health", __name__)
logger = logging.getLogger("pdfa.flask.health")


@health_bp.get("/")
def landing():
    """Render the landing page with wrapper health status."""

    started = time.perf_counter()
    health_payload: dict[str, object] = {}
    is_healthy = False
    error_message = ""

    try:
        health_payload = current_app.mcp_client.call("get_system_health", {})
        health_status = str(health_payload.get("health_status", "")).upper()
        is_healthy = health_status in {"CONNECTED", "HEALTHY", "UP", "OK"}
        if not is_healthy and str(health_payload.get("status", "")).lower() == "success":
            is_healthy = True
    except MCPClientError as exc:
        error_message = exc.message
        health_payload = {
            "status": "error",
            "health_status": "UNAVAILABLE",
            "health_status_description": "The backend is currently unavailable.",
        }

    logger.info(
        json.dumps(
            {
                "event": "flask.health.check.completed",
                "tool_name": "get_system_health",
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "workflow_name": session.get("active_workflow_name"),
                "username": session.get("user_id"),
                "is_healthy": is_healthy,
                "error": error_message,
            }
        )
    )

    return render_template(
        "landing.html",
        is_healthy=is_healthy,
        health_payload=health_payload,
        health_error=error_message,
    )